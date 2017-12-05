import argparse
import logging
from multiprocessing import Process

import pandas as pd
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from fooltrader import settings
from fooltrader.api.quote import get_security_list, get_latest_download_trading_date, get_trading_dates, \
    get_available_tick_dates
from fooltrader.settings import STOCK_START_CODE, STOCK_END_CODE
from fooltrader.spiders.security_list_spider import SecurityListSpider
from fooltrader.spiders.stock_kdata_spider_163 import StockKdataSpider163
from fooltrader.spiders.stock_tick_spider import StockTickSpider

logger = logging.getLogger(__name__)


def crawl(spider, setting):
    process = CrawlerProcess({**get_project_settings(), **setting})
    process.crawl(spider)
    process.start()


def process_crawl(spider, setting):
    p = Process(target=crawl, args=(spider, setting))
    p.start()
    p.join(5 * 60)


def crawl_stock_data(start_code=STOCK_START_CODE, end_code=STOCK_END_CODE):
    # 更新股票列表
    # TODO:看是否有必要判断有新股上市，目前每天抓一次列表，问题不大
    if False:
        logger.info('download stock list start')
        process_crawl(SecurityListSpider, {})
        logger.info('download stock list finish')

    for _, security_item in get_security_list(start=start_code, end=end_code).iterrows():
        # 抓取日K线
        logger.info("{} get kdata start".format(security_item['code']))
        start_date = get_latest_download_trading_date(security_item)
        end_date = pd.Timestamp.today()
        if start_date > end_date:
            logger.info("{} kdata is ok".format(security_item['code']))
        else:
            process_crawl(StockKdataSpider163, {"security_item": security_item,
                                                "start_date": start_date,
                                                "end_date": end_date})
            logger.info("{} get kdata end".format(security_item['code']))

        # 抓取tick
        base_dates = set(get_trading_dates(security_item))
        tick_dates = {x for x in base_dates if x >= settings.START_TICK_DATE}
        diff_dates = tick_dates - set(get_available_tick_dates(security_item))

        if diff_dates:
            logger.info("{} get tick start".format(security_item['code']))
            process_crawl(StockTickSpider, {"security_item": security_item,
                                            "trading_dates": diff_dates})
            logger.info("{} get tick end".format(security_item['code']))
        else:
            logger.info("{} tick is ok".format(security_item['code']))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start_code', default='000001', help='the stock start code to be crawled')
    parser.add_argument('-e', '--end_code', default='666666', help='the stock end code to be crawled')

    args = parser.parse_args()

    crawl_stock_data(args.start_code, args.end_code)
