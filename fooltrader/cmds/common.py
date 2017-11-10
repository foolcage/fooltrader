import logging
import os

import pandas as pd

from fooltrader.api.api import get_security_list
from fooltrader.contract import data_contract
from fooltrader.contract.data_contract import KDATA_COLUMN, KDATA_COLUMN_FQ
from fooltrader.contract.files_contract import get_kdata_path_csv, get_kdata_dir_csv, get_tick_dir, get_tick_path_csv, \
    get_trading_dates_path, get_kdata_dir
from fooltrader.utils.utils import sina_tick_to_csv

logger = logging.getLogger(__name__)


# 抓取k线时会自动生成交易日期json，如果出错，可以用该脚本手动生成
def init_trading_dates(security_item):
    try:
        dates = pd.Series()

        the_dir = get_kdata_dir_csv(security_item)
        files = [os.path.join(the_dir, f) for f in os.listdir(the_dir) if os.path.isfile(os.path.join(the_dir, f))]

        for f in files:
            df = pd.read_csv(f)
            dates = dates.append(df['timestamp'], ignore_index=True)
        dates = dates.sort_values()

        dates.to_json(get_trading_dates_path(security_item), orient='values')
        logger.info('init_trading_dates for item:{}'.format(security_item))
    except Exception as e:
        logger.error(
            'init_trading_dates for item:{},error:{}'.format(security_item, e))


def init_all_traing_dates():
    for _, item in get_security_list().iterrows():
        init_trading_dates(item)


def remove_old_json():
    for index, security_item in get_security_list().iterrows():
        for fuquan in ('bfq', 'hfq'):
            dir = get_kdata_dir_csv(security_item, fuquan)
            if os.path.exists(dir):
                files = [os.path.join(dir, f) for f in os.listdir(dir) if
                         ('json' in f and os.path.isfile(os.path.join(dir, f)))]
                for f in files:
                    logger.info("remove {}".format(f))
                    os.remove(f)


def legacy_tick_to_csv():
    for index, security_item in get_security_list().iterrows():
        dir = get_tick_dir(security_item)
        if os.path.exists(dir):
            files = [os.path.join(dir, f) for f in os.listdir(dir) if
                     ('xls' in f and 'lock' not in f and 'error' not in f and os.path.isfile(os.path.join(dir, f)))]
            for f in files:
                try:
                    the_date = os.path.splitext(os.path.basename(f))[0]
                    csv_path = get_tick_path_csv(security_item, the_date)
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
                    the_date = os.path.basename(f).split(".")[0]
                    csv_path = get_tick_path_csv(security_item, the_date)
                    if not os.path.exists(csv_path):
                        logger.info("{} to {}".format(f, csv_path))
                        sina_tick_to_csv(security_item, f, the_date)
                except Exception as e:
                    logger.warn(e)
                    os.rename(f, f + ".fatal")


def legacy_kdata_to_csv():
    for index, security_item in get_security_list().iterrows():
        for fuquan in (True, False):
            dir = get_kdata_dir(security_item, fuquan)
            if os.path.exists(dir):
                files = [os.path.join(dir, f) for f in os.listdir(dir) if
                         ('all' not in f and 'json' in f and os.path.isfile(os.path.join(dir, f)))]

                for f in files:
                    tmp = os.path.basename(f).split('_')
                    if fuquan:
                        csv_path = get_kdata_path_csv(security_item, tmp[0], tmp[1], 'hfq')
                        if not os.path.exists(csv_path):
                            df = pd.read_json(f, dtype={'code': str})
                            logger.info("{} to {}".format(f, csv_path))

                            df = df.loc[:,
                                 ['timestamp', 'code', 'low', 'open', 'close', 'high', 'volume', 'turnover',
                                  'securityId',
                                  'fuquan']]
                            df.columns = KDATA_COLUMN_FQ

                            df.to_csv(csv_path, index=False)
                    else:
                        csv_path = get_kdata_path_csv(security_item, tmp[0], tmp[1], 'bfq')
                        if not os.path.exists(csv_path):
                            df = pd.read_json(f, dtype={'code': str})
                            logger.info("{} to {}".format(f, csv_path))

                            df = df.loc[:, KDATA_COLUMN]

                            df.to_csv(csv_path, index=False)


def merge_kdata_to_one():
    for index, security_item in get_security_list().iterrows():
        for fuquan in ('bfq', 'hfq'):
            if fuquan == 'hfq':
                df = pd.DataFrame(
                    columns=data_contract.KDATA_COLUMN_FQ)
            else:
                df = pd.DataFrame(
                    columns=data_contract.KDATA_COLUMN)

            dir = get_kdata_dir_csv(security_item, fuquan=fuquan)

            if os.path.exists(dir):
                files = [os.path.join(dir, f) for f in os.listdir(dir) if
                         ('day' not in f and 'csv' in f and os.path.isfile(os.path.join(dir, f)))]
                for f in files:
                    df = df.append(pd.read_csv(f, dtype=str), ignore_index=True)
            df = df.set_index(df['timestamp'])
            df = df.sort_index()
            dayk_path = get_kdata_path_csv(security_item, fuquan=fuquan)
            logger.info("{} to {}".format(security_item['code'], dayk_path))
            # merge_to_current_kdata(security_item, df, fuquan=fuquan)
            df.to_csv(dayk_path, index=False)


if __name__ == '__main__':
    pd.set_option('expand_frame_repr', False)
    # merge_kdata_to_one()
    # handle_error_tick()
    legacy_kdata_to_csv()
