import datetime
import logging
import os

import pandas as pd

from fooltrader import settings
from fooltrader.contract import data_contract
from fooltrader.contract import files_contract
from fooltrader.contract.files_contract import get_kdata_dir_csv, get_kdata_path_csv
from fooltrader.datasource import tdx
from fooltrader.settings import STOCK_START_CODE, STOCK_END_CODE
from fooltrader.utils.utils import get_file_name

logger = logging.getLogger(__name__)


# meta
def get_security_list(security_type='stock', exchanges=['sh', 'sz'], start=STOCK_START_CODE, end=STOCK_END_CODE):
    df = pd.DataFrame()
    for exchange in exchanges:
        df1 = pd.read_csv(files_contract.get_security_list_path(security_type, exchange), converters={'code': str})
        df = df.append(df1, ignore_index=True)
    df = df[df["code"] <= end]
    df = df[df["code"] >= start]
    return df


def get_security_item(code):
    df = get_security_list(start=code, end=code)
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
            yield parse_tick(tick_path)


def parse_tick(tick_path):
    if os.path.isfile(tick_path):
        df = pd.read_csv(tick_path)
        df['timestamp'] = get_file_name(tick_path) + " " + df['timestamp']
        df = df.set_index(df['timestamp'])
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        return df


def get_available_tick_dates(security_item):
    dir = files_contract.get_tick_dir(security_item)
    return [get_file_name(f) for f in os.listdir(dir)]


# kdata
def get_kdata(security_item, the_date=None, start=None, end=None, fuquan=None, dtype=None):
    the_path = files_contract.get_kdata_path_csv(security_item, fuquan=fuquan)
    if os.path.isfile(the_path):
        if not dtype:
            dtype = {"code": str}
        df = pd.read_csv(the_path, dtype=dtype)
        df = df.set_index(df['timestamp'])
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        if the_date:
            return df[the_date]

        if not start:
            start = security_item['listDate']
        if not end:
            end = datetime.datetime.today()

        df.loc[start:end]
        return df
    return pd.DataFrame()


def get_trading_dates(security_item, dtype='list', ignore_today=True):
    df = get_kdata(security_item,fuquan='hfq')
    if dtype is 'list':
        dates = df.index.strftime('%Y-%m-%d').tolist()
        if ignore_today:
            dates = [the_date for the_date in dates if the_date != datetime.datetime.today().strftime('%Y-%m-%d')]
            return dates
    return df.index


def kdata_exist(security_item, year, quarter, fuquan=None):
    df = get_kdata(security_item, fuquan=fuquan)
    if "{}Q{}".format(year, quarter) in df.index:
        return True
    return False


# TODO:use join
def merge_to_current_kdata(security_item, df, fuquan='bfq'):
    df = df.set_index(df['timestamp'])
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()

    df1 = get_kdata(security_item, fuquan=fuquan, dtype=str)
    df1 = df1.append(df)

    df1 = df1.drop_duplicates(subset='timestamp', keep='last')
    df1 = df1.sort_index()

    the_path = files_contract.get_kdata_path_csv(security_item, fuquan=fuquan)
    df1.to_csv(the_path, index=False)


def merge_kdata_to_one(replace=False):
    for index, security_item in get_security_list().iterrows():
        for fuquan in ('bfq', 'hfq'):
            dayk_path = get_kdata_path_csv(security_item, fuquan=fuquan)
            if fuquan == 'hfq':
                df = pd.DataFrame(
                    columns=data_contract.KDATA_COLUMN_FQ)
            else:
                df = pd.DataFrame(
                    columns=data_contract.KDATA_COLUMN)

            the_dir = get_kdata_dir_csv(security_item, fuquan=fuquan)

            if os.path.exists(the_dir):
                files = [os.path.join(the_dir, f) for f in os.listdir(the_dir) if
                         (f != 'dayk.csv' and os.path.isfile(os.path.join(the_dir, f)))]
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


def remove_quarter_kdata():
    for index, security_item in get_security_list().iterrows():
        for fuquan in ('bfq', 'hfq'):
            dir = get_kdata_dir_csv(security_item, fuquan)
            if os.path.exists(dir):
                files = [os.path.join(dir, f) for f in os.listdir(dir) if
                         (f != 'dayk.csv' and os.path.isfile(os.path.join(dir, f)))]
                for f in files:
                    logger.info("remove {}".format(f))
                    os.remove(f)


# tick
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
    df2 = df2.set_index(df2['timestamp'])
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
