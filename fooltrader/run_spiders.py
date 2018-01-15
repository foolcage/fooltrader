import os

from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from twisted.internet import defer
from twisted.internet import reactor

from fooltrader import settings
from fooltrader.api.quote import get_security_list
from fooltrader.contract.files_contract import get_finance_dir, get_tick_dir, get_event_dir, \
    get_kdata_dir
from fooltrader.spiders.security_list_spider import SecurityListSpider

configure_logging()

# int_proxy()

runner = CrawlerRunner(get_project_settings())


@defer.inlineCallbacks
def crawl():
    yield runner.crawl(SecurityListSpider)
    # yield runner.crawl(StockKdataSpider163)
    # yield runner.crawl(StockTradingDateSpider)
    # yield runner.crawl(StockKDataSpiderTHS)
    # yield runner.crawl(StockKDataSpider)

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
