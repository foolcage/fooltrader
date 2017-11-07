import json
import logging
import os

import pandas as pd

from fooltrader.api.api import get_security_list
from fooltrader.contract.files_contract import get_kdata_path_new, get_kdata_dir_new, get_tick_dir, get_tick_path_csv
from fooltrader.utils.utils import get_kdata_dir, \
    get_trading_dates_path, get_security_items, init_env

logger = logging.getLogger(__name__)


# 抓取k线时会自动生成交易日期json，如果出错，可以用该脚本手动生成
def init_trading_dates(security_item):
    dates = []

    dir = get_kdata_dir(security_item)
    files = [os.path.join(dir, f) for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]

    for f in files:
        with open(f) as data_file:
            items = json.load(data_file)
            for k_item in items:
                dates.append(k_item['timestamp'])
    dates.sort()
    try:
        with open(get_trading_dates_path(security_item), "w") as f:
            json.dump(dates, f)
        logger.info('init_trading_dates for item:{}'.format(security_item))
    except Exception as e:
        logger.error(
            'init_trading_dates for item:{},error:{}'.format(security_item, e))


def init_all_traing_dates():
    for item in get_security_items():
        init_trading_dates(item)


{
    "turnover": "57888237",
    "type": "stock",
    "low": "24.650",
    "timestamp": "1999-12-30",
    "high": "24.990",
    "code": "600000",
    "securityId": "stock_sh_600000",
    "open": "24.900",
    "level": "DAY",
    "close": "24.750",
    "volume": "2333200"
}


def remove_old_json():
    for index, security_item in get_security_list().iterrows():
        for fuquan in ('bfq', 'hfq'):
            dir = get_kdata_dir_new(security_item, fuquan)
            if os.path.exists(dir):
                files = [os.path.join(dir, f) for f in os.listdir(dir) if
                         ('json' in f and os.path.isfile(os.path.join(dir, f)))]
                for f in files:
                    logger.info("remove {}".format(f))
                    os.remove(f)


def direction_to_int(direction):
    if direction == '买盘':
        return 1
    elif direction == '卖盘':
        return -1
    else:
        return 0


def legacy_tick_to_csv():
    for index, security_item in get_security_list().iterrows():
        dir = get_tick_dir(security_item)
        if os.path.exists(dir):
            files = [os.path.join(dir, f) for f in os.listdir(dir) if
                     ('xls' in f and 'lock' not in f and os.path.isfile(os.path.join(dir, f)))]
            for f in files:
                the_date = os.path.splitext(os.path.basename(f))[0]
                csv_path = get_tick_path_csv(security_item, the_date)
                logger.info("{} to {}".format(f, csv_path))
                df = pd.read_csv(f, sep='\s+', encoding='GB2312')
                df = df.loc[:, ['成交时间', '成交价', '成交量(手)', '成交额(元)', '性质']]
                df.columns = ['timestamp', 'price', 'volume', 'turnover', 'direction']
                df['direction'] = df['direction'].apply(lambda x: direction_to_int(x))
                df.to_csv(csv_path, index=False)


def legacy_kdata_to_csv():
    for index, security_item in get_security_list().iterrows():
        for fuquan in (True, False):
            dir = get_kdata_dir(security_item, fuquan)
            if os.path.exists(dir):
                files = [os.path.join(dir, f) for f in os.listdir(dir) if
                         ('all' not in f and 'json' in f and os.path.isfile(os.path.join(dir, f)))]

                for f in files:
                    tmp = os.path.basename(f).split('_')
                    df = pd.read_json(f)
                    if fuquan:
                        logger.info("{} to {}".format(f, get_kdata_path_new(security_item, tmp[0], tmp[1], 'hfq')))

                        df = df.loc[:,
                             ['timestamp', 'code', 'low', 'open', 'close', 'high', 'volume', 'turnover', 'securityId',
                              'fuquan']]
                        df.columns = ['timestamp', 'code', 'low', 'open', 'close', 'high', 'volume', 'turnover',
                                      'securityId', 'factor']

                        df.to_csv(get_kdata_path_new(security_item, tmp[0], tmp[1], 'hfq'), index=False)
                    else:
                        logger.info("{} to {}".format(f, get_kdata_path_new(security_item, tmp[0], tmp[1], 'bfq')))

                        df = df.loc[:,
                             ['timestamp', 'code', 'low', 'open', 'close', 'high', 'volume', 'turnover', 'securityId']]

                        df.to_csv(get_kdata_path_new(security_item, tmp[0], tmp[1], 'bfq'), index=False)


if __name__ == '__main__':
    init_env()
    legacy_tick_to_csv()
