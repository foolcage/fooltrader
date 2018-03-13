# -*- coding: utf-8 -*-

import datetime
import logging
import os
from ast import literal_eval

import numpy as np
import pandas as pd

from fooltrader.consts import CHINA_STOCK_INDEX, USA_STOCK_INDEX
from fooltrader.contract import data_contract
from fooltrader.contract import files_contract
from fooltrader.contract.files_contract import get_kdata_dir, get_kdata_path
from fooltrader.settings import US_STOCK_CODES
from fooltrader.utils.utils import get_file_name, to_time_str

logger = logging.getLogger(__name__)


def convert_to_list_if_need(input):
    if input and "[" in input:
        return literal_eval(input)
    else:
        return input


# meta
def get_security_list(security_type='stock', exchanges=['sh', 'sz'], start=None, end=None,
                      mode='simple', start_date=None, codes=None):
    """
    get security list.

    Parameters
    ----------
    security_type : str
        {‘stock’, 'future'},default: stock
    exchanges : list
        ['sh', 'sz','nasdaq','nyse','amex'],default: ['sh','sz']
    start : str
        the start code,default:None
        only works when exchanges is ['sh','sz']
    end : str
        the end code,default:None
        only works when exchanges is ['sh','sz']
    mode : str
        whether parse more security info,{'simple','es'},default:'simple'
    start_date : Timestamp str or Timestamp
        the filter for start list date,default:None
    codes : list
        the exact codes to query,default:None

    Returns
    -------
    DataFrame
        the security list

    """
    if security_type == 'stock':
        df = pd.DataFrame()
        df_usa = pd.DataFrame()
        for exchange in exchanges:
            the_path = files_contract.get_security_list_path(security_type, exchange)
            if os.path.exists(the_path):
                if exchange == 'sh' or exchange == 'sz':
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
                elif exchange == 'nasdaq':
                    df_usa = pd.read_csv(the_path, dtype=str)

    elif security_type == 'index':
        df = pd.DataFrame(CHINA_STOCK_INDEX)
        df_usa = pd.DataFrame()
        if 'nasdaq' in exchanges:
            df_usa = pd.DataFrame(USA_STOCK_INDEX)

    if df.size > 0:
        if start:
            df = df[df["code"] <= end]
        if end:
            df = df[df["code"] >= start]
        if start_date:
            df['listDate'] = pd.to_datetime(df['listDate'])
            df = df[df['listDate'] >= pd.Timestamp(start_date)]

        df = df.set_index(df['code'], drop=False)

    if df_usa.size > 0:
        df_usa = df_usa.set_index(df_usa['code'], drop=False)

        if codes:
            df_usa = df_usa.loc[codes]

    df = df.append(df_usa, ignore_index=True)
    return df


def _get_security_item(code=None, id=None, the_type='stock'):
    """
    get the security item.

    Parameters
    ----------
    code : str
        the security code,default: None
    id : str
        the security id,default: None

    the_type : str
        the security type

    Returns
    -------
    DataFrame
        the security item

    """
    df = get_security_list(security_type=the_type)
    if id:
        df = df.set_index(df['id'])
        return df.loc[id,]
    if code:
        df = df.set_index(df['code'])
    return df.loc[code,]


def to_security_item(security_item):
    if type(security_item) == str:
        if 'stock' in security_item:
            security_item = _get_security_item(id=security_item, the_type='stock')
        elif 'index' in security_item:
            security_item = _get_security_item(id=security_item, the_type='index')
        else:
            security_item = _get_security_item(code=security_item)
    return security_item


# tick
def get_ticks(security_item, the_date=None, start=None, end=None):
    """
    get the ticks.

    Parameters
    ----------
    security_item : SecurityItem or str
        the security item,id or code
    the_date : TimeStamp str or TimeStamp
        get the tick for the exact date
    start : TimeStamp str or TimeStamp
        start date
    end: TimeStamp str or TimeStamp
        end date

    Yields
    -------
    DataFrame

    """

    security_item = to_security_item(security_item)

    if the_date:
        tick_path = files_contract.get_tick_path(security_item, the_date)
        yield _parse_tick(tick_path, security_item)
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
            yield _parse_tick(tick_path, security_item)


def _parse_tick(tick_path, security_item):
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
    """
    get kdata.

    Parameters
    ----------
    security_item : SecurityItem or str
        the security item,id or code
    the_date : TimeStamp str or TimeStamp
        get the kdata for the exact date
    start_date : TimeStamp str or TimeStamp
        start date
    end_date : TimeStamp str or TimeStamp
        end date
    fuquan : str
        {"qfq","hfq","bfq"},default:"bfq"
    dtype : type
        the data type for the csv column,default: None
    source : str
        the data source,{'163','sina'},default: '163'
    level : str or int
        the kdata level,{1,5,15,30,60,'day','week','month'},default : 'day'

    Returns
    -------
    DataFrame

    """

    security_item = to_security_item(security_item)

    # 163的数据是合并过的,有复权因子,都存在'bfq'目录下,只需从一个地方取数据,并做相应转换
    if source == '163':
        the_path = files_contract.get_kdata_path(security_item, source=source, fuquan='bfq')
    else:
        the_path = files_contract.get_kdata_path(security_item, source=source, fuquan=fuquan)

    if os.path.isfile(the_path):
        if not dtype:
            dtype = {"code": str, 'timestamp': str}
        df = pd.read_csv(the_path, dtype=dtype)

        df.timestamp = df.timestamp.apply(lambda x: to_time_str(x))
        df = df.set_index(df['timestamp'], drop=False)
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        if the_date:
            if the_date in df.index:
                return df.loc[the_date]
            else:
                return pd.DataFrame()

        if not start_date:
            if security_item['type'] == 'stock':
                if type(security_item['listDate']) != str and np.isnan(security_item['listDate']):
                    start_date = '2002-01-01'
                else:
                    start_date = security_item['listDate']
            else:
                start_date = datetime.datetime.today() - datetime.timedelta(days=30)
        if not end_date:
            end_date = datetime.datetime.today()

        if start_date and end_date:
            df = df.loc[start_date:end_date]

        #
        if source == '163' and security_item['type'] == 'stock':
            if fuquan == 'bfq':
                return df
            if 'factor' in df.columns:
                current_factor = df.tail(1).factor.iat[0]
                # 后复权是不变的
                df.close *= df.factor
                df.open *= df.factor
                df.high *= df.factor
                df.low *= df.factor
                if fuquan == 'qfq':
                    # 前复权需要根据最新的factor往回算
                    df.close /= current_factor
                    df.open /= current_factor
                    df.high /= current_factor
                    df.low /= current_factor
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
    print(get_security_list(security_type='stock', exchanges=['nasdaq'], codes=US_STOCK_CODES))
    # item = {"code": "000001", "type": "stock", "exchange": "sz"}
    # assert kdata_exist(item, 1991, 2) == True
    # assert kdata_exist(item, 1991, 3) == True
    # assert kdata_exist(item, 1991, 4) == True
    # assert kdata_exist(item, 1991, 2) == True
    # assert kdata_exist(item, 1990, 1) == False
    # assert kdata_exist(item, 2017, 1) == False
    #
    # df1 = get_kdata(item,
    #                 datetime.datetime.strptime('1991-04-01', settings.TIME_FORMAT_DAY),
    #                 datetime.datetime.strptime('1991-12-31', settings.TIME_FORMAT_DAY))
    # df1 = df1.set_index(df1['timestamp'])
    # df1 = df1.sort_index()
    # print(df1)
    #
    # df2 = tdx.get_tdx_kdata(item, '1991-04-01', '1991-12-31')
    # df2 = df2.set_index(df2['timestamp'], drop=False)
    # df2 = df2.sort_index()
    # print(df2)
    #
    # for _, data in df1.iterrows():
    #     if data['timestamp'] in df2.index:
    #         data2 = df2.loc[data['timestamp']]
    #         assert data2["low"] == data["low"]
    #         assert data2["open"] == data["open"]
    #         assert data2["high"] == data["high"]
    #         assert data2["close"] == data["close"]
    #         assert data2["volume"] == data["volume"]
    #         try:
    #             assert data2["turnover"] == data["turnover"]
    #         except Exception as e:
    #             print(data2["turnover"])
    #             print(data["turnover"])
