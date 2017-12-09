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
from fooltrader.proxy.proxy_manager import int_proxy
from fooltrader.spiders.stock_kdata_spider_163 import StockKdataSpider163

configure_logging()

# int_proxy()

runner = CrawlerRunner(get_project_settings())


def mkdir_for_security(item):
    finance_dir = get_finance_dir(item)
    if not os.path.exists(finance_dir):
        os.makedirs(finance_dir)

    tick_dir = get_tick_dir(item)
    if not os.path.exists(tick_dir):
        os.makedirs(tick_dir)

    event_dir = get_event_dir(item)
    if not os.path.exists(event_dir):
        os.makedirs(event_dir)

    bfq_kdata_dir = get_kdata_dir(item, 'bfq')
    if not os.path.exists(bfq_kdata_dir):
        os.makedirs(bfq_kdata_dir)

    hfq_kdata_dir = get_kdata_dir(item, 'hfq')
    if not os.path.exists(hfq_kdata_dir):
        os.makedirs(hfq_kdata_dir)


def init_env():
    if not os.path.exists(settings.FILES_STORE):
        os.makedirs(settings.FILES_STORE)
    for _, item in get_security_list().iterrows():
        mkdir_for_security(item)


init_env()


@defer.inlineCallbacks
def crawl():
    # yield runner.crawl(SecurityListSpider)
    yield runner.crawl(StockKdataSpider163)
    # yield runner.crawl(StockTradingDateSpider)
    # yield runner.crawl(StockKDataSpiderTHS)
    # yield runner.crawl(StockKDataSpider)

    # yield runner.crawl(StockTickSpider)
    # yield runner.crawl(StockFinanceSpider)
    # yield runner.crawl(StockGNSpider)
    # yield runner.crawl(StockForecastSpider)
    # yield runner.crawl(ProxySpider)

    reactor.stop()


crawl()

reactor.run()  # the script will block here until the last crawl call is finished

# if __name__ == '__main__':
#     init_env()
