import logging
import os
import shutil

import pandas as pd

from fooltrader.api.hq import get_security_list
from fooltrader.contract import data_contract
from fooltrader.contract.data_contract import KDATA_COLUMN, KDATA_COLUMN_FQ
from fooltrader.contract.files_contract import get_kdata_path_csv, get_kdata_dir_csv, get_tick_dir, get_tick_path_csv, \
    get_kdata_dir
from fooltrader.utils.utils import sina_tick_to_csv

logger = logging.getLogger(__name__)


# 该脚本是用来转换以前抓的数据的,转换完成后就没有用了
# 请不要在其他地方引用里面的函数

def remove_old_tick():
    for index, security_item in get_security_list().iterrows():
        dir = get_tick_dir(security_item)
        if os.path.exists(dir):
            files = [os.path.join(dir, f) for f in os.listdir(dir) if
                     ('xls' in f and 'lock' not in f and 'error' not in f and os.path.isfile(os.path.join(dir, f)))]
            for f in files:
                logger.info("remove {}".format(f))
                os.remove(f)


def remove_old_kdata():
    for index, security_item in get_security_list().iterrows():
        for fuquan in (True, False):
            dir = get_kdata_dir(security_item, fuquan)
            if os.path.exists(dir):
                if fuquan:
                    logger.info("remove {}".format(dir))
                    shutil.rmtree(dir)
                else:
                    files = [os.path.join(dir, f) for f in os.listdir(dir) if
                             ('dayk.json' in f and os.path.isfile(os.path.join(dir, f)))]

                    for f in files:
                        logger.info("remove {}".format(f))
                        os.remove(f)

    for index, security_item in get_security_list().iterrows():
        for fuquan in ('bfq', 'hfq'):
            dir = get_kdata_dir_csv(security_item, fuquan)
            if os.path.exists(dir):
                files = [os.path.join(dir, f) for f in os.listdir(dir) if
                         ('dayk' not in f and os.path.isfile(os.path.join(dir, f)))]
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
            dayk_path = get_kdata_path_csv(security_item, fuquan=fuquan)
            if not os.path.exists(dayk_path):
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
                if df.size > 0:
                    df = df.set_index(df['timestamp'])
                    df.index = pd.to_datetime(df.index)
                    df = df.sort_index()
                    logger.info("{} to {}".format(security_item['code'], dayk_path))
                    # merge_to_current_kdata(security_item, df, fuquan=fuquan)
                    df.to_csv(dayk_path, index=False)


def check_convert_result():
    for index, security_item in get_security_list().iterrows():
        for fuquan in ('bfq', 'hfq'):
            dayk_path = get_kdata_path_csv(security_item, fuquan=fuquan)
            if os.path.exists(dayk_path):
                df_result = pd.read_csv(dayk_path)

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
                        df = df.append(pd.read_csv(f), ignore_index=True)
                    assert_df(df, df_result)
                    logger.info("{} merge as one ok".format(security_item['code']))


def assert_df(df1, df2):
    df1 = df1.set_index(df1['timestamp'])
    df1.index = pd.to_datetime(df1.index)
    df1 = df1.sort_index()

    df2 = df2.set_index(df2['timestamp'])
    df2 = df2.sort_index()
    df2.index = pd.to_datetime(df2.index)

    assert df1.index.equals(df2.index)

    for the_date in df1.index:
        assert df1.loc[the_date].equals(df2.loc[the_date])


def check_result():
    for index, security_item in get_security_list().iterrows():
        for fuquan in ('bfq', 'hfq'):
            dayk_path = get_kdata_path_csv(security_item, fuquan=fuquan)
            if not os.path.exists(dayk_path):
                logger.warn("{} no {} kdata csv?".format(security_item['code'], fuquan))

        dir = get_tick_dir(security_item)
        if os.path.exists(dir):
            files = [os.path.join(dir, f) for f in os.listdir(dir) if
                     ('csv' in f and os.path.isfile(os.path.join(dir, f)))]
            if not files:
                logger.warn("{} no tick csv?".format(security_item['code']))


if __name__ == '__main__':
    pd.set_option('expand_frame_repr', False)
    check_result()
