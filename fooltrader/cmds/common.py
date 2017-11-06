import json
import logging
import os

from fooltrader.api.api import get_security_list
from fooltrader.contract.files_contract import get_kdata_path
from fooltrader.utils.utils import get_kdata_dir, \
    get_trading_dates_path, get_security_items

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


def legacy_to_new():
    for index, security_item in get_security_list().iterrows():
        get_kdata_path()

if __name__ == '__main__':
    legacy_to_new()
