# -*- coding: utf-8 -*-

import datetime
import json
import logging
import os
import re
from ast import literal_eval

import numpy as np
import pandas as pd

from fooltrader.consts import CHINA_STOCK_INDEX, USA_STOCK_INDEX
from fooltrader.contract import data_contract
from fooltrader.contract import files_contract
from fooltrader.contract.data_contract import get_future_name, KDATA_COLUMN_FUTURE
from fooltrader.contract.files_contract import get_kdata_dir, get_kdata_path, get_exchange_cache_dir, \
    get_security_list_path, get_exchange_trading_calendar_path
from fooltrader.datamanager.zipdata import unzip
from fooltrader.utils.utils import get_file_name, to_time_str, drop_duplicate

logger = logging.getLogger(__name__)


def convert_to_list_if_need(input):
    if input and "[" in input:
        return literal_eval(input)
    else:
        return input


def get_support_exchanges():
    return ['sh', 'sz', 'shfe', 'dce', 'zce']


# meta
def get_security_list(security_type='stock', exchanges=['sh', 'sz'], start=None, end=None,
                      mode='simple', start_list_date=None, codes=None):
    """
    get security list.

    Parameters
    ----------
    security_type : str
        {‘stock’, 'future'},default: stock
    exchanges : list
        ['sh', 'sz','nasdaq','nyse','amex','shfe','dce','zce'],default: ['sh','sz']
    start : str
        the start code,default:None
        only works when exchanges is ['sh','sz']
    end : str
        the end code,default:None
        only works when exchanges is ['sh','sz']
    mode : str
        whether parse more security info,{'simple','es'},default:'simple'
    start_list_date : Timestamp str or Timestamp
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
            the_path = get_security_list_path(security_type, exchange)
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
    elif security_type == 'future':
        df = pd.DataFrame()
        for exchange in exchanges:
            the_path = get_security_list_path(security_type, exchange)
            if os.path.exists(the_path):
                df1 = pd.read_csv(the_path,
                                  converters={'code': str})
                df = df.append(df1, ignore_index=True)
        return df

    if df.size > 0:
        if start:
            df = df[df["code"] >= start]
        if end:
            df = df[df["code"] <= end]
        if start_list_date:
            df['listDate'] = pd.to_datetime(df['listDate'])
            df = df[df['listDate'] >= pd.Timestamp(start_list_date)]

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
    if the_type == 'future':
        exchange = ['shfe']
    else:
        exchange = ['sh', 'sz']

    df = get_security_list(security_type=the_type, exchanges=exchange)
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
        elif 'future' in security_item:
            security_item = _get_security_item(id=security_item, the_type='future')
        else:
            # 中国期货
            if re.match("^[A-Za-z]{2}\d{4}", security_item):
                security_item = _get_security_item(code=security_item, the_type='future')
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
            elif security_item['type'] == 'index':
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


def get_trading_calendar(security_type='future', exchange='shfe'):
    the_path = get_exchange_trading_calendar_path(security_type, exchange)

    trading_dates = []
    if os.path.exists(the_path):
        with open(the_path) as data_file:
            trading_dates = json.load(data_file)
    return trading_dates


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


def parse_shfe_day_data(force_parse=False):
    cache_dir = get_exchange_cache_dir(security_type='future', exchange='shfe', the_year=datetime.datetime.today().year,
                                       data_type="day_kdata")
    the_parsed_path = os.path.join(cache_dir, 'parsed')
    the_parsed = []
    if os.path.exists(the_parsed_path):
        with open(the_parsed_path) as data_file:
            the_parsed = json.load(data_file)

    if force_parse:
        the_dates = [f for f in os.listdir(cache_dir) if
                     f != 'parsed' and f]
    else:
        the_dates = [f for f in os.listdir(cache_dir) if
                     f != 'parsed' and f not in the_parsed]

    for the_date in the_dates:
        the_path = os.path.join(cache_dir, the_date)
        logger.info("start handling {}".format(the_path))

        with open(the_path, 'r', encoding='UTF8') as f:
            tmp_str = f.read()
            the_json = json.loads(tmp_str)
            the_datas = the_json['o_curinstrument']
            # 日期,代码,名称,最低,开盘,收盘,最高,成交量(手),成交额(元),唯一标识,前收盘,涨跌额,涨跌幅(%),持仓量,结算价,前结算,涨跌额(按结算价),涨跌幅(按结算价)
            KDATA_COLUMN_FUTURE = ['timestamp', 'code', 'name', 'low', 'open', 'close', 'high', 'volume', 'turnover',
                                   'securityId',
                                   'preClose', 'change', 'changePct', 'openInterest', 'settlement', 'preSettlement',
                                   'change1',
                                   'changePct1']
            for the_data in the_datas:
                # {'CLOSEPRICE': 11480,
                #  'DELIVERYMONTH': '1809',
                #  'HIGHESTPRICE': 11555,
                #  'LOWESTPRICE': 11320,
                #  'OPENINTEREST': 425692,
                #  'OPENINTERESTCHG': 3918,
                #  'OPENPRICE': 11495,
                #  'ORDERNO': 0,
                #  'PRESETTLEMENTPRICE': 11545,
                #  'PRODUCTID': 'ru_f    ',
                #  'PRODUCTNAME': '天然橡胶            ',
                #  'PRODUCTSORTNO': 100,
                #  'SETTLEMENTPRICE': 11465,
                #  'VOLUME': 456574,
                #  'ZD1_CHG': -65,
                #  'ZD2_CHG': -80}

                if not re.match("\d{4}", the_data['DELIVERYMONTH']):
                    continue

                code = "{}{}".format(the_data['PRODUCTID'][:the_data['PRODUCTID'].index('_')],
                                     the_data['DELIVERYMONTH'])
                logger.info("start handling {} for {}".format(code, the_date))

                name = get_future_name(code)
                security_id = "future_shfe_{}".format(code)

                security_list = get_security_list(security_type='future', exchanges=['shfe'])

                logger.info("start handling {} for {}".format(code, the_date))
                security_item = {'code': code,
                                 'name': name,
                                 'id': security_id,
                                 'exchange': 'shfe',
                                 'type': 'future'}
                # 检查是否需要保存合约meta
                if security_list is not None and 'code' in security_list.columns:
                    security_list = security_list.set_index(security_list['code'], drop=False)
                if code not in security_list.index:
                    security_list = security_list.append(security_item, ignore_index=True)
                    security_list.to_csv(get_security_list_path('future', 'shfe'), index=False)

                kdata_path = get_kdata_path(item=security_item, source='exchange')
                # TODO：这些逻辑应该统一处理
                kdata_dir = get_kdata_dir(item=security_item)
                if not os.path.exists(kdata_dir):
                    os.makedirs(kdata_dir)

                if os.path.exists(kdata_path):
                    saved_df = pd.read_csv(kdata_path, dtype=str)
                    saved_df = saved_df.set_index(saved_df['timestamp'], drop=False)
                else:
                    saved_df = pd.DataFrame()

                if saved_df.empty or the_date not in saved_df.index:
                    low_price = the_data['LOWESTPRICE']
                    if not low_price:
                        low_price = 0
                    open_price = the_data['OPENPRICE']
                    if not open_price:
                        open_price = 0
                    close_price = the_data['CLOSEPRICE']
                    if not close_price:
                        close_price = 0
                    high_price = the_data['HIGHESTPRICE']
                    if not high_price:
                        high_price = 0
                    volume = the_data['VOLUME']
                    if not volume:
                        volume = 0

                    if type(the_data['ZD1_CHG']) == str:
                        change = 0
                    else:
                        change = the_data['ZD1_CHG']

                    if type(the_data['ZD2_CHG']) == str:
                        change1 = 0
                    else:
                        change1 = the_data['ZD2_CHG']

                    pre_close = close_price - change
                    pre_settlement = the_data['PRESETTLEMENTPRICE']

                    # 首日交易
                    if pre_close != 0:
                        change_pct = change / pre_close
                    else:
                        change_pct = 0
                    if pre_settlement != 0:
                        change_pct1 = change1 / pre_settlement
                    else:
                        change_pct1 = 0

                    the_json = {
                        "timestamp": to_time_str(the_date),
                        "code": code,
                        "name": name,
                        "low": low_price,
                        "open": open_price,
                        "close": close_price,
                        "high": high_price,
                        "volume": volume,
                        # 成交额为估算
                        "turnover": (low_price + open_price + close_price + high_price / 4) * volume,
                        "securityId": security_id,
                        "preClose": pre_close,
                        "change": change,
                        "changePct": change_pct,
                        "openInterest": the_data['OPENINTEREST'],
                        "settlement": the_data['SETTLEMENTPRICE'],
                        "preSettlement": the_data['PRESETTLEMENTPRICE'],
                        "change1": change1,
                        "changePct1": change_pct1
                    }
                    saved_df = saved_df.append(the_json, ignore_index=True)
                    saved_df = saved_df.loc[:, KDATA_COLUMN_FUTURE]
                    saved_df = saved_df.drop_duplicates(subset='timestamp', keep='last')
                    saved_df = saved_df.set_index(saved_df['timestamp'], drop=False)
                    saved_df.index = pd.to_datetime(saved_df.index)
                    saved_df = saved_df.sort_index()
                    saved_df.to_csv(kdata_path, index=False)

                    logger.info("end handling {} for {}".format(code, the_date))

                    if the_date not in the_parsed:
                        the_parsed.append(the_date)
        if the_parsed:
            result_list = drop_duplicate(the_parsed)
            result_list = sorted(result_list)

            with open(the_parsed_path, 'w') as outfile:
                json.dump(result_list, outfile)
        logger.info("end handling {}".format(the_path))


def parse_shfe_data(force_parse=False):
    the_dir = get_exchange_cache_dir(security_type='future', exchange='shfe')

    need_parse_files = []

    for the_zip_file in [os.path.join(the_dir, f) for f in
                         os.listdir(the_dir) if f.endswith('.zip')
                         ]:
        dst_file = the_zip_file.replace('.zip', ".xls")

        if not os.path.exists(dst_file):
            dst_dir = the_zip_file.replace('.zip', "")
            os.makedirs(dst_dir)

            unzip(the_zip_file, dst_dir)
            files = [os.path.join(dst_dir, f) for f in
                     os.listdir(dst_dir) if f.endswith('.xls')
                     ]
            if len(files) == 1:
                os.rename(files[0], dst_file)
            need_parse_files.append(dst_file)

    if force_parse:
        need_parse_files = [os.path.join(the_dir, f) for f in
                            os.listdir(the_dir) if f.endswith('.xls')
                            ]
    for the_file in need_parse_files:
        logger.info("parse {}".format(the_file))

        df = pd.read_excel(the_file, skiprows=2, skip_footer=4, index_col='合约', converters={'日期': str})
        df.index = pd.Series(df.index).fillna(method='ffill')
        df = df.loc[:, ['日期', '前收盘', '前结算', '开盘价', '最高价', '最低价', '收盘价', '结算价', '涨跌1', '涨跌2', '成交量', '成交金额', '持仓量']]
        df.columns = ['timestamp', 'preClose', 'preSettlement', 'open', 'high', 'low', 'close', 'settlement',
                      'change', 'change1', 'volume', 'turnover', 'openInterest']

        # 日期格式统一，方便导入es
        # df.timestamp = df.timestamp.apply(lambda x: to_time_str(x))

        unique_index = df.index.drop_duplicates()

        security_list = get_security_list(security_type='future', exchanges=['shfe'])

        for the_contract in unique_index:
            logger.info("start handling {} in {}".format(the_contract, the_file))
            security_item = {'code': the_contract,
                             'name': get_future_name(the_contract),
                             'id': 'future_{}_{}'.format('shfe', the_contract),
                             'exchange': 'shfe',
                             'type': 'future'}
            # 检查是否需要保存合约meta
            if security_list is not None and 'code' in security_list.columns:
                security_list = security_list.set_index(security_list['code'], drop=False)
            if the_contract not in security_list.index:
                security_list = security_list.append(security_item, ignore_index=True)
                security_list = security_list.sort_index()
                security_list.to_csv(get_security_list_path('future', 'shfe'), index=False)

            the_df = df.loc[the_contract,]
            the_df['code'] = the_contract
            the_df['name'] = get_future_name(the_contract)
            the_df['securityId'] = 'future_{}_{}'.format('shfe', the_contract)
            the_df['changePct'] = the_df['change'] / the_df['preClose']
            the_df['changePct1'] = the_df['change1'] / the_df['preSettlement']

            kdata_path = get_kdata_path(item=security_item, source='exchange')
            # TODO：这些逻辑应该统一处理
            kdata_dir = get_kdata_dir(item=security_item)
            if not os.path.exists(kdata_dir):
                os.makedirs(kdata_dir)

            if os.path.exists(kdata_path):
                saved_df = pd.read_csv(kdata_path, dtype=str)
            else:
                saved_df = pd.DataFrame()

            saved_df = saved_df.append(the_df, ignore_index=True)
            saved_df = saved_df.loc[:, KDATA_COLUMN_FUTURE]
            saved_df = saved_df.drop_duplicates(subset='timestamp', keep='last')
            saved_df = saved_df.set_index(saved_df['timestamp'], drop=False)
            saved_df.index = pd.to_datetime(saved_df.index)
            saved_df = saved_df.sort_index()
            saved_df.to_csv(kdata_path, index=False)

            logger.info("end handling {} in {}".format(the_contract, the_file))


if __name__ == '__main__':
    # print(get_kdata('000001'))
    # parse_shfe_day_data()
    print(get_kdata('ag1801', source='exchange'))
    # print(get_security_list(security_type='stock', exchanges=['nasdaq'], codes=US_STOCK_CODES))
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
