import argparse
import logging
import os
from multiprocessing import Process

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from fooltrader import settings
from fooltrader.settings import STATUS_SHOW_NOT_OK_DATE
from fooltrader.spiders.security_list_spider import SecurityListSpider
from fooltrader.spiders.stock_kdata_spider import StockKDataSpider
from fooltrader.spiders.stock_tick_spider import StockTickSpider
from fooltrader.spiders.stock_trading_date_spider import StockTradingDateSpider
from fooltrader.utils.utils import get_sh_stock_list_path, get_sz_stock_list_path, get_security_items, \
    get_trading_dates, get_downloaded_tick_dates, get_trading_dates_path_sse

logger = logging.getLogger(__name__)


def crawl(spider, setting):
    process = CrawlerProcess({**get_project_settings(), **setting})
    process.crawl(spider)
    process.start()


def process_crawl(spider, setting):
    p = Process(target=crawl, args=(spider, setting))
    p.start()
    p.join(5 * 60)


def check_data_integrity():
    status = {}
    # check security list
    if not os.path.exists(get_sh_stock_list_path()) or not os.path.exists(get_sz_stock_list_path()):
        logger.info('------download stock list at first------')
        process_crawl(SecurityListSpider)

    for security_item in get_security_items('000001', '666666'):
        status.setdefault(security_item['code'], {})
        # check trading date
        if not os.path.exists(get_trading_dates_path_sse(security_item)):
            logger.info("------need to download {} trading date------".format(security_item['code']))
            process_crawl(StockTradingDateSpider, {"security_item": security_item})
        else:
            base_dates = set(get_trading_dates(security_item, True))
            dates = set(get_trading_dates(security_item, False))
            diff1 = base_dates - dates
            if diff1:
                if STATUS_SHOW_NOT_OK_DATE:
                    logger.info("------{} kdata not ok for dates:{}------".format(security_item['code'], diff1))
                else:
                    logger.info("------{} kdata not ok------".format(security_item['code']))

                logger.info("------try to fix {} kdata------".format(security_item['code']))

                the_dates = list(diff1)
                the_dates.sort()
                process_crawl(StockKDataSpider, {"security_item": security_item,
                                                 "start_date": the_dates[0],
                                                 "end_date": the_dates[-1]})
            else:
                logger.info("------{} kdata ok------".format(security_item['code']))
                diff2 = dates - base_dates
                # this should not happen
                if diff2:
                    if STATUS_SHOW_NOT_OK_DATE:
                        status[security_item['code']] = {'base trading dates': 'not ok?:{}'.format(diff2)}
                    else:
                        status[security_item['code']] = {'base trading dates': 'not ok?'}

            tick_dates = {x for x in base_dates if x >= settings.START_TICK_DATE}
            diff3 = tick_dates - set(get_downloaded_tick_dates(security_item))
            if diff3:
                if STATUS_SHOW_NOT_OK_DATE:
                    logger.info("------{} tick not ok for dates:{}------".format(security_item['code'], diff3))
                else:
                    logger.info("------{} tick not ok------".format(security_item['code']))

                logger.info("------try to fix {} tick------".format(security_item['code']))

                process_crawl(StockTickSpider, {"security_item": security_item,
                                                "trading_dates": diff3})
            else:
                logger.info("------{} tick ok------".format(security_item['code']))


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
    check_data_integrity()
