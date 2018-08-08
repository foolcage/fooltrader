# -*- coding: utf-8 -*-

import datetime
import json
import logging
import os
import re
from ast import literal_eval

import pandas as pd

from fooltrader.consts import CHINA_STOCK_SH_INDEX, CHINA_STOCK_SZ_INDEX, USA_STOCK_NASDAQ_INDEX, \
    SECURITY_TYPE_MAP_EXCHANGES
from fooltrader.contract import files_contract
from fooltrader.contract.data_contract import get_future_name, KDATA_FUTURE_COL
from fooltrader.contract.files_contract import get_kdata_dir, get_kdata_path, get_exchange_cache_dir, \
    get_security_list_path, get_exchange_trading_calendar_path, adjust_source
from fooltrader.datamanager.zipdata import unzip
from fooltrader.utils import pd_utils
from fooltrader.utils.pd_utils import kdata_df_save, df_for_date_range
from fooltrader.utils.utils import get_file_name, to_time_str, drop_duplicate

logger = logging.getLogger(__name__)


def convert_to_list_if_need(input):
    if input and "[" in input:
        return literal_eval(input)
    else:
        return input


# meta
def get_security_list(security_type='stock', exchanges=None, start_code=None, end_code=None,
                      mode='simple', start_list_date=None, codes=None):
    """
    get security list.

    Parameters
    ----------
    security_type : str
        {‘stock’, 'future'},default: stock
    exchanges : str or list
        ['sh', 'sz','nasdaq','nyse','amex','shfe','dce','zce'],default: ['sh','sz']
    start_code : str
        the start code,work with end,default:None
        if using codes,it would be ignored
    end_code : str
        the end code,works with start,default:None
        if using codes,it would be ignored
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
    df = pd.DataFrame()
    if type(exchanges) == str:
        exchanges = [exchanges]

    if not exchanges:
        exchanges = SECURITY_TYPE_MAP_EXCHANGES[security_type]

    if security_type == 'index':
        df = df.append(pd.DataFrame(CHINA_STOCK_SH_INDEX), ignore_index=True)
        df = df.append(pd.DataFrame(CHINA_STOCK_SZ_INDEX), ignore_index=True)
        df = df.append(pd.DataFrame(USA_STOCK_NASDAQ_INDEX), ignore_index=True)
    else:
        for exchange in exchanges:
            the_path = get_security_list_path(security_type, exchange)
            if os.path.exists(the_path):
                converters = None

                if mode == 'es' and security_type == 'stock':
                    converters = {'code': str,
                                  'sinaIndustry': convert_to_list_if_need,
                                  'sinaConcept': convert_to_list_if_need,
                                  'sinaArea': convert_to_list_if_need}
                if converters:
                    df = df.append(pd.read_csv(the_path, converters=converters), ignore_index=True)
                else:
                    df = df.append(pd.read_csv(the_path, dtype=str), ignore_index=True)

    if not df.empty > 0:
        df = df_for_date_range(df, start_date=start_list_date)

        df = df.set_index(df['code'], drop=False)
        df = df.sort_index()

        if codes:
            df = df[df["code"].isin(codes)]
        elif start_code and end_code:
            df = df[(df["code"] >= start_code) & (df["code"] <= end_code)]

        if security_type != 'cryptocurrency':
            df = df.drop_duplicates(subset='code', keep='last')

    return df


def _get_security_item(security_type, exchanges, code=None):
    """
    get the security item.

    Parameters
    ----------
    code : str
        the security code,default: None

    security_type : str
        the security type

    exchanges : list
        the exchanges

    Returns
    -------
    DataFrame
        the security item

    """
    df = get_security_list(security_type=security_type, exchanges=exchanges)

    if not df.empty:
        df = df.set_index(df['code'])
        return df.loc[code,]
    return None


def to_security_item(security_item, exchange=None):
    if type(security_item) == str:
        if exchange:
            return _get_security_item('cryptocurrency', [exchange], security_item)

        id_match = re.match(r'(stock|index|future|cryptocurrency)_([a-z]{2,20})_([a-zA-Z0-9\-]+)',
                            security_item)
        if id_match:
            return _get_security_item(security_type=id_match.group(1), exchanges=[id_match.group(2)],
                                      code=id_match.group(3))

        # 中国期货
        if re.match(r'^[A-Za-z]{2}\d{4}', security_item):
            return _get_security_item(code=security_item, security_type='future', exchanges=['shfe'])

        # 中国股票
        if re.match(r'\d{6}', security_item):
            return _get_security_item(code=security_item, security_type='stock', exchanges=['sh', 'sz'])

        # 美国股票
        if re.match(r'[A-Z]{2,20}', security_item):
            return _get_security_item(code=security_item, security_type='stock', exchanges=['nasdaq'])
    return security_item


# tick
def get_ticks(security_item, the_date=None, start_date=None, end_date=None):
    """
    get the ticks.

    Parameters
    ----------
    security_item : SecurityItem or str
        the security item,id or code
    the_date : TimeStamp str or TimeStamp
        get the tick for the exact date
    start_date : TimeStamp str or TimeStamp
        start date
    end_date: TimeStamp str or TimeStamp
        end date

    Yields
    -------
    DataFrame

    """

    security_item = to_security_item(security_item)

    if the_date:
        the_date = to_time_str(the_date)
        tick_path = files_contract.get_tick_path(security_item, the_date)
        yield _parse_tick(tick_path, security_item)
    else:
        tick_dir = files_contract.get_tick_dir(security_item)
        if start_date or end_date:
            if not start_date:
                start_date = security_item['listDate']
            if not end_date:
                end_date = datetime.datetime.today()
            tick_paths = [os.path.join(tick_dir, f) for f in
                          os.listdir(tick_dir) if
                          get_file_name(f) in pd.date_range(start=start_date, end=end_date)]
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
def get_kdata(security_item, exchange=None, the_date=None, start_date=None, end_date=None, fuquan='bfq', source=None,
              level='day', generate_id=False):
    """
    get kdata.

    Parameters
    ----------
    security_item : SecurityItem or str
        the security item,id or code

    exchange : str
        the exchange,set this for cryptocurrency

    the_date : TimeStamp str or TimeStamp
        get the kdata for the exact date
    start_date : TimeStamp str or TimeStamp
        start date
    end_date : TimeStamp str or TimeStamp
        end date
    fuquan : str
        {"qfq","hfq","bfq"},default:"bfq"
    source : str
        the data source,{'163','sina','exchange'},just used for internal merge
    level : str or int
        the kdata level,{1,5,15,30,60,'day','week','month'},default : 'day'

    Returns
    -------
    DataFrame

    """

    # 由于数字货币的交易所太多，必须指定exchange
    security_item = to_security_item(security_item, exchange)

    source = adjust_source(security_item, source)

    # 163的数据是合并过的,有复权因子,都存在'bfq'目录下,只需从一个地方取数据,并做相应转换
    if source == '163':
        the_path = files_contract.get_kdata_path(security_item, source=source, fuquan='bfq')
    else:
        the_path = files_contract.get_kdata_path(security_item, source=source, fuquan=fuquan)

    if os.path.isfile(the_path):
        df = pd_utils.pd_read_csv(the_path, generate_id=generate_id)

        if 'factor' in df.columns and source == '163' and security_item['type'] == 'stock':
            df_kdata_has_factor = df[df['factor'].notna()]
            if df_kdata_has_factor.shape[0] > 0:
                latest_factor = df_kdata_has_factor.tail(1).factor.iat[0]
            else:
                latest_factor = None

        if the_date:
            if the_date in df.index:
                df = df.loc[the_date:the_date, :]
            else:
                return None
        else:
            if start_date or end_date:
                df = df_for_date_range(df, start_date=start_date, end_date=end_date)

        # 复权处理
        if source == '163' and security_item['type'] == 'stock':
            if 'factor' in df.columns:
                # 后复权是不变的
                df['hfqClose'] = df.close * df.factor
                df['hfqOpen'] = df.open * df.factor
                df['hfqHigh'] = df.high * df.factor
                df['hfqLow'] = df.low * df.factor

                # 前复权需要根据最新的factor往回算,当前价格不变
                if latest_factor:
                    df['qfqClose'] = df.hfqClose / latest_factor
                    df['qfqOpen'] = df.hfqOpen / latest_factor
                    df['qfqHigh'] = df.hfqHigh / latest_factor
                    df['qfqLow'] = df.hfqLow / latest_factor
                else:
                    logger.exception("missing latest factor for {}".format(security_item['id']))

        return df
    return pd.DataFrame()


def get_latest_download_trading_date(security_item, return_next=True, source=None):
    df = get_kdata(security_item, source=source)
    if len(df) == 0:
        return pd.Timestamp(security_item['listDate']), df
    if return_next:
        return df.index[-1] + pd.DateOffset(1), df
    else:
        return df.index[-1], df


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
    if pd.Period("{}Q{}".format(year, quarter)).end_time < df.index.max():
        return True
    return False


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
            if (not security_list.empty) and ('code' in security_list.columns):
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
            saved_df = saved_df.loc[:, KDATA_FUTURE_COL]

            if not saved_df.empty:
                kdata_df_save(saved_df, kdata_path)

            logger.info("end handling {} in {}".format(the_contract, the_file))


if __name__ == '__main__':
    print(get_kdata('ag1801', source='exchange'))
