import json
import logging
import os

from fooltrader.settings import STOCK_START_CODE, STOCK_END_CODE
from fooltrader.utils.utils import get_sh_stock_list_path, get_sz_stock_list_path, get_security_item, get_kdata_dir, \
    get_trading_dates_path

logger = logging.getLogger(__name__)


# 抓取k线时会自动生成交易日期json，如果出错，可以用该脚本手动生成
def init_trading_dates():
    dates = []
    stock_files = (get_sh_stock_list_path(), get_sz_stock_list_path())
    for stock_file in stock_files:
        for item in get_security_item(stock_file):
            if STOCK_START_CODE <= item['code'] <= STOCK_END_CODE:
                dir = get_kdata_dir(item)
                files = [os.path.join(dir, f) for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]

                for f in files:
                    with open(f) as data_file:
                        items = json.load(data_file)
                        for k_item in items:
                            dates.append(k_item['timestamp'])
                dates.sort()
                try:
                    with open(get_trading_dates_path(item), "w") as f:
                        json.dump(dates, f)
                    logger.info('init_trading_dates for item:{}'.format(item))
                except Exception as e:
                    logger.error(
                        'init_trading_dates for item:{},error:{}'.format(item, e))


if __name__ == '__main__':
    init_trading_dates()
