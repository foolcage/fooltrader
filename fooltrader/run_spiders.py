# -*- coding: utf-8 -*-

import os

from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from twisted.internet import defer
from twisted.internet import reactor

from fooltrader import settings
from fooltrader.contract.files_contract import get_finance_dir, get_tick_dir, get_event_dir, \
    get_kdata_dir
from fooltrader.spiders.america.america_stock_finance_spider import AmericaStockFinanceSpider

from fooltrader.spiders.america.america_stock_kdata_spider_163 import AmericaStockKdataSpider
from fooltrader.spiders.chinastock.stock_kdata_sina_spider import StockKDataSinaSpider

configure_logging()

# int_proxy()

runner = CrawlerRunner(get_project_settings())


@defer.inlineCallbacks
def crawl():
    yield runner.crawl(StockKDataSinaSpider)
    # yield runner.crawl(AmericaStockKdataSpider)
    # yield runner.crawl(AmericaStockFinanceSpider)
    # yield runner.crawl(Sp500Spider)
    # yield runner.crawl(SecurityListSpider)
    # yield runner.crawl(StockKdataSpider163)
    # yield runner.crawl(StockTradingDateSpider)
    # yield runner.crawl(StockKDataSpiderTHS)
    # yield runner.crawl(ShfeTradingCalendarSpider)

    # yield runner.crawl(StockTickSpider)
    # yield runner.crawl(StockFinanceSpider)
    # yield runner.crawl(StockFinanceReportEventSpider)
    # yield runner.crawl(StockGNSpider)
    # yield runner.crawl(StockForecastSpider)
    # yield runner.crawl(ProxySpider)

    reactor.stop()


crawl()

reactor.run()  # the script will block here until the last crawl call is finished

# if __name__ == '__main__':
#     init_env()
