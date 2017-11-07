import argparse
import logging
import os
from multiprocessing import Process

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from fooltrader import settings
from fooltrader.api.api import get_security_list
from fooltrader.cmds.common import init_trading_dates
from fooltrader.settings import STATUS_SHOW_NOT_OK_DATE
from fooltrader.spiders import SecurityListSpider
from fooltrader.spiders import StockKDataSpider
from fooltrader.spiders import StockKDataSpiderTHS
from fooltrader.spiders import StockTickSpider
from fooltrader.spiders import StockTradingDateSpider
from fooltrader.utils.utils import get_sh_stock_list_path, get_sz_stock_list_path, get_trading_dates, \
    get_downloaded_tick_dates, get_trading_dates_path_sse, get_trading_dates_path_ths, \
    get_base_trading_dates, merge_ths_kdata

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
    # check security list
    if not os.path.exists(get_sh_stock_list_path()) or not os.path.exists(get_sz_stock_list_path()) or True:
        logger.info('------download stock list at first------')
        process_crawl(SecurityListSpider)

    for _, security_item in get_security_list().iterrows():
        # download base trading dates at first
        if not os.path.exists(get_trading_dates_path_sse(security_item)):
            logger.info("------need to download {} sse trading date------".format(security_item['code']))
            process_crawl(StockTradingDateSpider, {"security_item": security_item})
        if not os.path.exists(get_trading_dates_path_ths(security_item)):
            logger.info("------need to download {} ths trading date------".format(security_item['code']))
            process_crawl(StockKDataSpiderTHS, {"security_item": security_item})

        # compare kdata/tick with base trading dates and fix them
        base_dates = set(get_base_trading_dates(security_item))
        init_trading_dates(security_item)
        dates = set(get_trading_dates(security_item))
        diff1 = base_dates - dates
        if diff1:
            if STATUS_SHOW_NOT_OK_DATE:
                logger.info("------{} kdata not ok for dates:{}------".format(security_item['code'], diff1))
            else:
                logger.info("------{} kdata not ok------".format(security_item['code']))

            logger.info("------try to fix {} kdata------".format(security_item['code']))

            the_dates = list(diff1)
            the_dates.sort()
            merge_ths_kdata(security_item, the_dates)

            process_crawl(StockKDataSpider, {"security_item": security_item,
                                             "start_date": the_dates[0],
                                             "end_date": the_dates[-1]})

        else:
            logger.info("------{} kdata ok------".format(security_item['code']))
            diff2 = dates - base_dates
            # this should not happen
            if diff2:
                logger.info("{} base trading dates not ok?".format(security_item['id']))

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

parser.add_argument("cmd", choices=['check_data', 'check_kafka', 'check_es'])

args = parser.parse_args()

if args.cmd == 'check_data':
    check_data_integrity()
elif args.cmd == 'check_kafka':
    check_data_integrity()
