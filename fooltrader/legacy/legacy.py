# -*- coding: utf-8 -*-

import json
import logging
import os
import shutil

import pandas as pd

from fooltrader.api.technical import get_security_list
from fooltrader.contract import data_contract
from fooltrader.contract.data_contract import KDATA_COLUMN_SINA, KDATA_COLUMN_SINA_FQ, EVENT_STOCK_FINANCE_FORECAST_COL, \
    EVENT_STOCK_FINANCE_REPORT_COL
from fooltrader.contract.files_contract import get_kdata_dir, get_tick_dir, get_tick_path, \
    get_security_dir, get_kdata_path, get_trading_dates_path_163, get_event_dir, get_finance_forecast_event_path, \
    get_finance_report_event_path
from fooltrader.utils.utils import sina_tick_to_csv, get_file_name, get_year_quarter, get_datetime, to_time_str

logger = logging.getLogger(__name__)


# 该脚本是用来转换以前抓的数据的,转换完成后就没有用了
# 请不要在其他地方引用里面的函数

# 目前看同花顺的后复权和新浪的差别挺大，先以新浪的为准
def get_kdata_path_csv_ths(item, fuquan=None):
    if fuquan == 'qfq' or fuquan == 'hfq':
        return os.path.join(get_security_dir(item), 'kdata', '{}_ths.csv'.format(fuquan))
    else:
        return os.path.join(get_security_dir(item), 'kdata', 'ths.csv')


def get_kdata_path_ths(item, fuquan=False):
    if fuquan:
        return os.path.join(get_security_dir(item), 'ths_fuquan_dayk.json')
    else:
        return os.path.join(get_security_dir(item), 'ths_dayk.json')


def get_kdata_dir_old(item, fuquan=False):
    if fuquan:
        return os.path.join(get_security_dir(item), 'kdata', 'fuquan')
    else:
        return os.path.join(get_security_dir(item), 'kdata')


def get_kdata_path_old(item, year, quarter, fuquan):
    if fuquan:
        return os.path.join(get_kdata_dir_old(item, fuquan), '{}_{}_fuquan_dayk.json'.format(year, quarter))
    else:
        return os.path.join(get_kdata_dir_old(item), '{}_{}_dayk.json'.format(year, quarter))


def get_trading_dates_path(item):
    return os.path.join(get_security_dir(item), 'trading_dates.json')


def get_kdata_items(security_item, houfuquan=False):
    dir = get_kdata_dir_old(security_item, houfuquan)
    if os.path.exists(dir):
        files = [os.path.join(dir, f) for f in os.listdir(dir) if
                 (f != "all_dayk.json" and os.path.isfile(os.path.join(dir, f)))]

        for f in sorted(files):
            with open(f) as data_file:
                kdata_jsons = json.load(data_file)
                for kdata_json in reversed(kdata_jsons):
                    yield kdata_json


def merge_ths_kdata(security_item, dates):
    ths_kdata = {}
    ths_fuquan_kdata = {}

    try:
        with open(get_kdata_path_ths(security_item)) as data_file:
            ths_items = json.load(data_file)
            for item in ths_items:
                if item["timestamp"] in dates:
                    ths_kdata[item["timestamp"]] = item

        with open(get_kdata_path_ths(security_item, True)) as data_file:
            ths_items = json.load(data_file)
            for item in ths_items:
                if item["timestamp"] in dates:
                    ths_fuquan_kdata[item["timestamp"]] = item

        year_quarter_map_dates = {}
        for the_date in dates:
            year, quarter = get_year_quarter(get_datetime(the_date))
            year_quarter_map_dates.setdefault((year, quarter), [])
            year_quarter_map_dates.get((year, quarter)).append(the_date)

        for year, quarter in year_quarter_map_dates.keys():
            for fuquan in (False, True):
                data_path = get_kdata_path_old(security_item, year, quarter, fuquan)
                data_exist = os.path.isfile(data_path)
                if data_exist:
                    with open(data_path) as data_file:
                        k_items = json.load(data_file)
                        if fuquan:
                            for the_date in year_quarter_map_dates.get((year, quarter)):
                                k_items.append(ths_fuquan_kdata[the_date])
                        else:
                            for the_date in year_quarter_map_dates.get((year, quarter)):
                                k_items.append(ths_kdata[the_date])
                    k_items = sorted(k_items, key=lambda item: item["timestamp"], reverse=True)

                    with open(data_path, "w") as f:
                        json.dump(k_items, f)


    except Exception as e:
        logger.exception(e)


def remove_old_trading_dates():
    for index, security_item in get_security_list().iterrows():
        the_path = get_trading_dates_path(security_item)
        if os.path.exists(the_path):
            logger.info("remove {}".format(the_path))
            os.remove(the_path)


def remove_old_163_trading_dates():
    for index, security_item in get_security_list().iterrows():
        the_path = get_trading_dates_path_163(security_item)
        if os.path.exists(the_path):
            logger.info("remove {}".format(the_path))
            os.remove(the_path)


def remove_old_tick():
    for index, security_item in get_security_list().iterrows():
        dir = get_tick_dir(security_item)
        if os.path.exists(dir):
            files = [os.path.join(dir, f) for f in os.listdir(dir) if
                     ('xls' in f and 'lock' not in f and 'error' not in f and os.path.isfile(os.path.join(dir, f)))]
            for f in files:
                logger.info("remove {}".format(f))
                os.remove(f)


def is_available_tick(path):
    encoding = 'GB2312'
    try:
        with open(path, encoding=encoding) as fr:
            line = fr.readline()
            return u'成交时间', u'成交价', u'价格变动', u'成交量(手)', u'成交额(元)', u'性质' == line.split()
    except Exception:
        return False


def remove_old_kdata():
    for index, security_item in get_security_list().iterrows():
        for fuquan in (True, False):
            dir = get_kdata_dir_old(security_item, fuquan)
            if os.path.exists(dir):
                if fuquan:
                    logger.info("remove {}".format(dir))
                    shutil.rmtree(dir)
                    # else:
                    #     files = [os.path.join(dir, f) for f in os.listdir(dir) if
                    #              ('dayk.json' in f and os.path.isfile(os.path.join(dir, f)))]
                    #
                    #     for f in files:
                    #         logger.info("remove {}".format(f))
                    #         os.remove(f)

                    # for index, security_item in get_security_list().iterrows():
                    #     for fuquan in ('bfq', 'hfq'):
                    #         dir = get_kdata_dir_csv(security_item, fuquan)
                    #         if os.path.exists(dir):
                    #             files = [os.path.join(dir, f) for f in os.listdir(dir) if
                    #                      ('dayk' not in f and os.path.isfile(os.path.join(dir, f)))]
                    #             for f in files:
                    #                 logger.info("remove {}".format(f))
                    #                 os.remove(f)


def legacy_tick_to_csv():
    for index, security_item in get_security_list().iterrows():
        dir = get_tick_dir(security_item)
        if os.path.exists(dir):
            files = [os.path.join(dir, f) for f in os.listdir(dir) if
                     ('xls' in f and 'lock' not in f and 'error' not in f and os.path.isfile(os.path.join(dir, f)))]
            for f in files:
                try:
                    the_date = get_file_name(f)
                    csv_path = get_tick_path(security_item, the_date)
                    if not os.path.exists(csv_path):
                        logger.info("{} to {}".format(f, csv_path))
                        sina_tick_to_csv(security_item, f, the_date)
                except Exception as e:
                    logger.warn(e)
                    os.rename(f, f + ".error")


def handle_error_tick():
    for index, security_item in get_security_list().iterrows():
        dir = get_tick_dir(security_item)
        if os.path.exists(dir):
            files = [os.path.join(dir, f) for f in os.listdir(dir) if
                     (('fatal' in f or 'error' in f) and os.path.isfile(os.path.join(dir, f)))]
            for f in files:
                try:
                    the_date = get_file_name(f)
                    csv_path = get_tick_path(security_item, the_date)
                    if not os.path.exists(csv_path):
                        logger.info("{} to {}".format(f, csv_path))
                        sina_tick_to_csv(security_item, f, the_date)
                except Exception as e:
                    logger.warn(e)
                    os.rename(f, f + ".fatal")


def legacy_kdata_to_csv():
    for index, security_item in get_security_list().iterrows():
        for fuquan in (True, False):
            dir = get_kdata_dir_old(security_item, fuquan)
            if os.path.exists(dir):
                files = [os.path.join(dir, f) for f in os.listdir(dir) if
                         ('all' not in f and 'json' in f and os.path.isfile(os.path.join(dir, f)))]

                for f in files:
                    tmp = os.path.basename(f).split('_')
                    if fuquan:
                        csv_path = get_kdata_path(security_item, tmp[0], tmp[1], 'hfq')
                        if not os.path.exists(csv_path):
                            df = pd.read_json(f, dtype={'code': str})
                            logger.info("{} to {}".format(f, csv_path))

                            df = df.loc[:,
                                 ['timestamp', 'code', 'low', 'open', 'close', 'high', 'volume', 'turnover',
                                  'securityId',
                                  'fuquan']]
                            df.columns = KDATA_COLUMN_SINA_FQ

                            df.to_csv(csv_path, index=False)
                    else:
                        csv_path = get_kdata_path(security_item, tmp[0], tmp[1], 'bfq')
                        if not os.path.exists(csv_path):
                            df = pd.read_json(f, dtype={'code': str})
                            logger.info("{} to {}".format(f, csv_path))

                            df = df.loc[:, KDATA_COLUMN_SINA]

                            df.to_csv(csv_path, index=False)


def check_convert_result():
    for index, security_item in get_security_list().iterrows():
        for fuquan in ('bfq', 'hfq'):
            dayk_path = get_kdata_path(security_item, fuquan=fuquan)
            if os.path.exists(dayk_path):
                df_result = pd.read_csv(dayk_path)

                if fuquan == 'hfq':
                    df = pd.DataFrame(
                        columns=data_contract.KDATA_COLUMN_SINA_FQ)
                else:
                    df = pd.DataFrame(
                        columns=data_contract.KDATA_COLUMN_SINA)

                dir = get_kdata_dir(security_item, fuquan=fuquan)

                if os.path.exists(dir):
                    files = [os.path.join(dir, f) for f in os.listdir(dir) if
                             ('day' not in f and 'csv' in f and os.path.isfile(os.path.join(dir, f)))]
                    for f in files:
                        df = df.append(pd.read_csv(f), ignore_index=True)
                    assert_df(df, df_result)
                    logger.info("{} merge as one ok".format(security_item['code']))


def assert_df(df1, df2):
    df1 = df1.set_index(df1['timestamp'], drop=False)
    df1.index = pd.to_datetime(df1.index)
    df1 = df1.sort_index()

    df2 = df2.set_index(df2['timestamp'], drop=False)
    df2 = df2.sort_index()
    df2.index = pd.to_datetime(df2.index)

    assert df1.index.equals(df2.index)

    for the_date in df1.index:
        assert df1.loc[the_date].equals(df2.loc[the_date])


def check_result():
    for index, security_item in get_security_list().iterrows():
        for fuquan in ('bfq', 'hfq'):
            dayk_path = get_kdata_path(security_item, fuquan=fuquan)
            if not os.path.exists(dayk_path):
                logger.warn(get_security_dir(security_item))

        dir = get_tick_dir(security_item)
        if os.path.exists(dir):
            files = [os.path.join(dir, f) for f in os.listdir(dir) if
                     ('csv' in f and os.path.isfile(os.path.join(dir, f)))]
            if not files:
                logger.warn(get_security_dir(security_item))


def get_forecast_event_path(item, event='forecast'):
    return os.path.join(get_event_dir(item), '{}.json'.format(event))


def forecast_event_to_csv():
    for index, security_item in get_security_list().iterrows():
        the_path = get_forecast_event_path(security_item)
        if os.path.exists(the_path):
            df = pd.read_json(get_forecast_event_path(security_item))
            df = df.rename(columns={'reportDate': 'timestamp'})
            df = df.loc[:, EVENT_STOCK_FINANCE_FORECAST_COL]
            df.to_csv(get_finance_forecast_event_path(security_item), index=False)
            logger.info("transform {} forecast event".format(security_item['code']))
            os.remove(the_path)


def finance_report_event_to_csv():
    for index, security_item in get_security_list().iterrows():
        the_path = get_finance_report_event_path(security_item)
        if os.path.exists(the_path):
            df = pd.read_csv(the_path)
            df = df.rename(columns={'reportEventDate': 'timestamp', 'reportDate': 'reportPeriod'})
            df = df.loc[:, EVENT_STOCK_FINANCE_REPORT_COL]
            df.to_csv(get_finance_report_event_path(security_item), index=False)
            logger.info("transform {} report event".format(security_item['code']))


def time_index_df(df):
    df = df.set_index(df['timestamp'], drop=False)
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    return df


def restore_kdata():
    for index, security_item in get_security_list(start_code='600000', end_code='600017').iterrows():
        path_163 = get_kdata_path(security_item, source='163', fuquan='bfq')
        df = pd.read_csv(path_163, dtype=str)
        df = time_index_df(df)

        if 'id' in df.columns:
            df = df.drop(['id'], axis=1)
        df = df[~df.index.duplicated(keep='first')]
        df.timestamp.apply(lambda x: to_time_str(x))
        df.to_csv(path_163, index=False)

        for fuquan in ('hfq', 'bfq'):
            path_sina = get_kdata_path(security_item, source='sina', fuquan=fuquan)
            df = pd.read_csv(path_sina, dtype=str)
            df = time_index_df(df)
            if 'id' in df.columns:
                df = df.drop(['id'], axis=1)
            df = df[~df.index.duplicated(keep='first')]
            df.timestamp = df.timestamp.apply(lambda x: to_time_str(x))
            df.to_csv(path_sina, index=False)


if __name__ == '__main__':
    pd.set_option('expand_frame_repr', False)
    # remove_old_trading_dates()
    # remove_old_kdata()
    # remove_old_tick()
    # forecast_event_to_csv()
    # finance_report_event_to_csv()
    restore_kdata()
