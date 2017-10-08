import argparse
import json
import logging
import os

from jsonmerge import merge
from scrapy.crawler import CrawlerProcess

from fooltrader.settings import STATUS_SHOW_NOT_OK_DATE
from fooltrader.spiders.security_list_spider import SecurityListSpider
from fooltrader.spiders.stock_kdata_spider import StockKDataSpider
from fooltrader.utils.utils import get_sh_stock_list_path, get_sz_stock_list_path, get_security_items, \
    get_kdata_path_ths, get_trading_dates_path_ths, get_trading_dates, get_downloaded_tick_dates, get_status_path

logger = logging.getLogger(__name__)


def crawl(*spiders):
    process = CrawlerProcess()
    for spider in spiders:
        process.crawl(spider)
    process.start()


def generate_status():
    status = {}
    if not os.path.exists(get_sh_stock_list_path()) or not os.path.exists(get_sz_stock_list_path()):
        return {'status': 'stock list not ok'}
    for security_item in get_security_items():
        status.setdefault(security_item['code'], {})
        if not os.path.exists(get_kdata_path_ths(security_item)) or not os.path.exists(
                get_trading_dates_path_ths(security_item)):
            status[security_item['code']] = {'ths kdata': 'not ok'}
        else:
            ths_dates = set(get_trading_dates(security_item, True))
            dates = set(get_trading_dates(security_item, False))
            diff1 = ths_dates - dates
            if diff1:
                if STATUS_SHOW_NOT_OK_DATE:
                    status[security_item['code']] = {'sina kdata': 'not ok:{}'.format(diff1)}
                else:
                    status[security_item['code']] = {'sina kdata': 'not ok'}
            else:
                diff2 = dates - ths_dates
                # this should not happen
                if diff2:
                    if STATUS_SHOW_NOT_OK_DATE:
                        status[security_item['code']] = {'ths kdata': 'not ok?:{}'.format(diff2)}
                    else:
                        status[security_item['code']] = {'ths kdata': 'not ok?'}

            diff3 = ths_dates - set(get_downloaded_tick_dates(security_item))
            if diff3:
                if STATUS_SHOW_NOT_OK_DATE:
                    status[security_item['code']] = merge(status[security_item['code']],
                                                          {'tick': 'not ok:{}'.format(diff3)})
                else:
                    status[security_item['code']] = merge(status[security_item['code']],
                                                          {'tick': 'not ok'})

        logger.info('{}:{}'.format(security_item['code'], status[security_item['code']]))

        with open(get_status_path(), "w") as f:
            json.dump(status, f)


parser = argparse.ArgumentParser()

parser.add_argument("-s", "--stock_list", action="store_true", help="download the stock list")

parser.add_argument("-k", "--kdata", action="store_true", help="download the stock kdata")

parser.add_argument("-c", "--check", action="store_true", help="check data")

args = parser.parse_args()

if args.stock_list:
    crawl(SecurityListSpider)

if args.kdata:
    crawl(StockKDataSpider)

if args.check:
    generate_status()
