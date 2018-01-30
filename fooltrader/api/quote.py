import datetime
import logging
import os
from ast import literal_eval

import pandas as pd

from fooltrader import settings
from fooltrader.consts import CHINA_STOCK_INDEX
from fooltrader.contract import data_contract
from fooltrader.contract import files_contract
from fooltrader.contract.files_contract import get_kdata_dir, get_kdata_path
from fooltrader.datasource import tdx
from fooltrader.utils.utils import get_file_name

logger = logging.getLogger(__name__)


def convert_to_list_if_need(input):
    if input and "[" in input:
        return literal_eval(input)
    else:
        return input


# meta
def get_security_list(security_type='stock', exchanges=['sh', 'sz'], start=None, end=None,
                      mode='simple', start_date=None):
    if security_type == 'stock':
        df = pd.DataFrame()
        for exchange in exchanges:
            the_path = files_contract.get_security_list_path(security_type, exchange)
            if os.path.exists(the_path):
                if mode == 'simple':
                    df1 = pd.read_csv(the_path,
                                      converters={'code': str})
                else:
                    df1 = pd.read_csv(the_path,
                                      converters={'code': str,
                                                  'sinaIndustry': convert_to_list_if_need,
                                                  'sinaConcept': convert_to_list_if_need,
                                                  'sinaArea': convert_to_list_if_need})
                df = df.append(df1, ignore_index=True)
    elif security_type == 'index':
        df = pd.DataFrame(CHINA_STOCK_INDEX)

    if df.size > 0:
        if start:
            df = df[df["code"] <= end]
        if end:
            df = df[df["code"] >= start]
        if start_date:
            df['listDate'] = pd.to_datetime(df['listDate'])
            df = df[df['listDate'] >= pd.Timestamp(start_date)]
        df = df.set_index(df['code'], drop=False)

    return df


def get_security_item(code=None, id=None):
    df = get_security_list()
    if id:
        df = df.set_index(df['id'])
        return df.loc[id,]
    if code:
        df = df.set_index(df['code'])
    return df.loc[code,]


# tick
def get_ticks(security_item, the_date=None, start=None, end=None):
    if the_date:
        tick_path = files_contract.get_tick_path(security_item, the_date)
        return parse_tick(tick_path)
    else:
        tick_dir = files_contract.get_tick_dir(security_item)
        if start or end:
            if not start:
                start = security_item['listDate']
            if not end:
                end = datetime.datetime.today()
            tick_paths = [os.path.join(tick_dir, f) for f in
                          os.listdir(tick_dir) if
                          get_file_name(f) in pd.date_range(start=start, end=end)]
        else:
            tick_paths = [os.path.join(tick_dir, f) for f in
                          os.listdir(tick_dir)]

        for tick_path in sorted(tick_paths):
            yield parse_tick(tick_path, security_item)


def parse_tick(tick_path, security_item):
    if os.path.isfile(tick_path):
        df = pd.read_csv(tick_path)
        df['timestamp'] = get_file_name(tick_path) + " " + df['timestamp']
        df = df.set_index(df['timestamp'], drop=False)
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        df['code'] = security_item['code']
        df['securityId'] = security_item['id']
        return df


def get_available_tick_dates(security_item):
    dir = files_contract.get_tick_dir(security_item)
    return [get_file_name(f) for f in os.listdir(dir)]


# kdata
def get_kdata(security_item, the_date=None, start_date=None, end_date=None, fuquan='bfq', dtype=None, source='163',
              level='day'):
    if type(security_item) == str:
        if 'stock' in security_item:
            security_item = get_security_item(id=security_item)
        else:
            security_item = get_security_item(code=security_item)

    the_path = files_contract.get_kdata_path(security_item, source=source, fuquan=fuquan)

    if os.path.isfile(the_path):
        if not dtype:
            dtype = {"code": str}
        df = pd.read_csv(the_path, dtype=dtype)
        df = df.set_index(df['timestamp'], drop=False)
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        if the_date:
            if the_date in df.index:
                return df.loc[the_date]
            else:
                return pd.DataFrame()

        if not start_date:
            start_date = security_item['listDate']
        if not end_date:
            end_date = datetime.datetime.today()

        df = df.loc[start_date:end_date]
        return df
    return pd.DataFrame()


def get_latest_download_trading_date(security_item, return_next=True, source='163'):
    df = get_kdata(security_item, source=source)
    if len(df) == 0:
        return pd.Timestamp(security_item['listDate'])
    if return_next:
        return df.index[-1] + pd.DateOffset(1)
    else:
        return df.index[-1]


def get_trading_dates(security_item, dtype='list', ignore_today=False, source='163', fuquan='bfq'):
    df = get_kdata(security_item, source=source, fuquan=fuquan)
    if dtype is 'list' and len(df.index) > 0:
        dates = df.index.strftime('%Y-%m-%d').tolist()
        if ignore_today:
            dates = [the_date for the_date in dates if the_date != datetime.datetime.today().strftime('%Y-%m-%d')]
            return dates
        return dates
    return df.index


def kdata_exist(security_item, year, quarter, fuquan=None, source='163'):
    df = get_kdata(security_item, fuquan=fuquan, source=source)
    if "{}Q{}".format(year, quarter) in df.index:
        return True
    return False


# TODO:use join
def merge_to_current_kdata(security_item, df, fuquan='bfq'):
    df = df.set_index(df['timestamp'], drop=False)
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()

    df1 = get_kdata(security_item, source='sina', fuquan=fuquan, dtype=str)
    df1 = df1.append(df)

    df1 = df1.drop_duplicates(subset='timestamp', keep='last')
    df1 = df1.sort_index()

    the_path = files_contract.get_kdata_path(security_item, source='sina', fuquan=fuquan)
    df1.to_csv(the_path, index=False)


def time_index_df(df):
    df = df.set_index(df['timestamp'])
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    return df


def add_factor_to_163(security_item):
    path_163 = get_kdata_path(security_item, source='163', fuquan='bfq')
    df_163 = pd.read_csv(path_163, dtype=str)
    df_163 = time_index_df(df_163)

    if 'factor' in df_163.columns:
        df = df_163[df_163['factor'].isna()]

        if df.empty:
            logger.info("{} 163 factor is ok", security_item['code'])
            return

    path_sina = get_kdata_path(security_item, source='sina', fuquan='hfq')
    df_sina = pd.read_csv(path_sina, dtype=str)
    df_sina = time_index_df(df_sina)

    df_163['factor'] = df_sina['factor']
    df_163.to_csv(path_163, index=False)


def merge_kdata_to_one(security_item=None, replace=False, fuquan='bfq'):
    if type(security_item) != 'NoneType':
        items = pd.DataFrame().append(security_item).iterrows()
    else:
        items = get_security_list().iterrows()

    if fuquan:
        fuquans = [fuquan]
    else:
        fuquans = ['bfq', 'hfq']

    for index, security_item in items:
        for fuquan in fuquans:
            dayk_path = get_kdata_path(security_item, source='sina', fuquan=fuquan)
            if fuquan == 'hfq':
                df = pd.DataFrame(
                    columns=data_contract.KDATA_COLUMN_FQ)
            else:
                df = pd.DataFrame(
                    columns=data_contract.KDATA_COLUMN)

            the_dir = get_kdata_dir(security_item, fuquan=fuquan)

            if os.path.exists(the_dir):
                files = [os.path.join(the_dir, f) for f in os.listdir(the_dir) if
                         ('dayk.csv' not in f and os.path.isfile(os.path.join(the_dir, f)))]
                for f in files:
                    df = df.append(pd.read_csv(f, dtype=str), ignore_index=True)
            if df.size > 0:
                df = df.set_index(df['timestamp'])
                df.index = pd.to_datetime(df.index)
                df = df.sort_index()
                logger.info("{} to {}".format(security_item['code'], dayk_path))
                if replace:
                    df.to_csv(dayk_path, index=False)
                else:
                    merge_to_current_kdata(security_item, df, fuquan=fuquan)

            for f in files:
                logger.info("remove {}".format(f))
                os.remove(f)

            if fuquan == 'hfq':
                add_factor_to_163(security_item)


if __name__ == '__main__':
    item = {"code": "000001", "type": "stock", "exchange": "sz"}
    assert kdata_exist(item, 1991, 2) == True
    assert kdata_exist(item, 1991, 3) == True
    assert kdata_exist(item, 1991, 4) == True
    assert kdata_exist(item, 1991, 2) == True
    assert kdata_exist(item, 1990, 1) == False
    assert kdata_exist(item, 2017, 1) == False

    df1 = get_kdata(item,
                    datetime.datetime.strptime('1991-04-01', settings.TIME_FORMAT_DAY),
                    datetime.datetime.strptime('1991-12-31', settings.TIME_FORMAT_DAY))
    df1 = df1.set_index(df1['timestamp'])
    df1 = df1.sort_index()
    print(df1)

    df2 = tdx.get_tdx_kdata(item, '1991-04-01', '1991-12-31')
    df2 = df2.set_index(df2['timestamp'], drop=False)
    df2 = df2.sort_index()
    print(df2)

    for _, data in df1.iterrows():
        if data['timestamp'] in df2.index:
            data2 = df2.loc[data['timestamp']]
            assert data2["low"] == data["low"]
            assert data2["open"] == data["open"]
            assert data2["high"] == data["high"]
            assert data2["close"] == data["close"]
            assert data2["volume"] == data["volume"]
            try:
                assert data2["turnover"] == data["turnover"]
            except Exception as e:
                print(data2["turnover"])
                print(data["turnover"])
