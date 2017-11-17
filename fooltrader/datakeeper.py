import logging
import os
from multiprocessing import Process

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from fooltrader import settings
from fooltrader.api.quote import get_security_list, get_trading_dates, get_available_tick_dates
from fooltrader.contract.files_contract import get_security_list_path
from fooltrader.datasource import tdx
from fooltrader.settings import STATUS_SHOW_NOT_OK_DATE
from fooltrader.spiders.security_list_spider import SecurityListSpider
from fooltrader.spiders.stock_kdata_spider import StockKDataSpider
from fooltrader.spiders.stock_kdata_spider_ths import StockKDataSpiderTHS
from fooltrader.spiders.stock_tick_spider import StockTickSpider
from fooltrader.spiders.stock_trading_date_spider import StockTradingDateSpider
from fooltrader.utils.utils import get_trading_dates_path_sse, get_trading_dates_path_ths, \
    get_base_trading_dates

# 检查数据的完整性

logger = logging.getLogger(__name__)


def crawl(spider, setting):
    process = CrawlerProcess({**get_project_settings(), **setting})
    process.crawl(spider)
    process.start()


def process_crawl(spider, setting):
    p = Process(target=crawl, args=(spider, setting))
    p.start()
    p.join(5 * 60)


# 校验历史数据的完整性算法，先从新浪数据获取数据，从证监会和同花顺获取交易日期
# 如果新浪数据的日期缺少，试图重新获取缺少的数据，如果获取不到，去tdx获取
# 不管如何，都生成符合contract的数据,数据源越多，数据质量就越高
FORCE_DOWNLOAD_SECURITY_LIST = True
FORCE_DOWNLOAD_SSE_TRADING_DATES = True
FORCE_DOWNLOAD_SSE_TRADING_DATES = True


def check_data_integrity():
    # check security list
    if not os.path.exists(get_security_list_path('stock', 'sh')) or not os.path.exists(
            get_security_list_path('stock', 'sz')):
        logger.info('------download stock list at first------')
        process_crawl(SecurityListSpider, {})

    for _, security_item in get_security_list().iterrows():
        # download base trading dates at first
        if not os.path.exists(get_trading_dates_path_sse(security_item)):
            logger.info("------need to download {} sse trading date------".format(security_item['code']))
            process_crawl(StockTradingDateSpider, {"security_item": security_item})
        # 暂时不用同花顺,缺少成交额数据
        if not os.path.exists(get_trading_dates_path_ths(security_item)) and False:
            logger.info("------need to download {} ths trading date------".format(security_item['code']))
            process_crawl(StockKDataSpiderTHS, {"security_item": security_item})

        # compare kdata/tick with base trading dates and fix them
        base_dates = set(get_base_trading_dates(security_item))
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

            # 试图从新浪修复
            process_crawl(StockKDataSpider, {"security_item": security_item,
                                             "trading_dates": the_dates})

            dates = set(get_trading_dates(security_item))
            diff1 = base_dates - dates
            # 试图从tdx修复
            if diff1:
                the_dates = list(diff1)
                the_dates.sort()
                tdx.save_tdx_kdata(security_item, the_dates)

        else:
            logger.info("------{} kdata ok------".format(security_item['code']))
            diff2 = dates - base_dates
            # this should not happen
            if diff2:
                logger.info("{} base trading dates not ok?".format(security_item['id']))

        tick_dates = {x for x in base_dates if x >= settings.START_TICK_DATE}
        diff3 = tick_dates - set(get_available_tick_dates(security_item))
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


# parser = argparse.ArgumentParser()
#
# parser.add_argument("cmd", choices=['check_data', 'check_kafka', 'check_es'])
#
# args = parser.parse_args()
#
# if args.cmd == 'check_data':
#     check_data_integrity()
# elif args.cmd == 'check_kafka':
#     check_data_integrity()
if __name__ == '__main__':
    check_data_integrity()
