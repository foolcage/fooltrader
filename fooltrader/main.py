import os

from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from twisted.internet import defer
from twisted.internet import reactor

from fooltrader import settings
from fooltrader.api.hq import get_security_list
from fooltrader.contract.files_contract import get_kdata_dir, get_finance_dir, get_tick_dir, get_event_dir, \
    get_kdata_dir_csv
from fooltrader.proxy.proxy_manager import int_proxy
from fooltrader.spiders.security_list_spider import SecurityListSpider
from fooltrader.spiders.stock_kdata_spider import StockKDataSpider
from fooltrader.spiders.stock_tick_spider import StockTickSpider
from fooltrader.utils.utils import setup_env

configure_logging()

setup_env()

int_proxy()

runner = CrawlerRunner(get_project_settings())


def mkdir_for_security(item):
    fuquan_kdata_dir = get_kdata_dir(item, True)
    if not os.path.exists(fuquan_kdata_dir):
        os.makedirs(fuquan_kdata_dir)

    finance_dir = get_finance_dir(item)
    if not os.path.exists(finance_dir):
        os.makedirs(finance_dir)

    tick_dir = get_tick_dir(item)
    if not os.path.exists(tick_dir):
        os.makedirs(tick_dir)

    event_dir = get_event_dir(item)
    if not os.path.exists(event_dir):
        os.makedirs(event_dir)

    bfq_kdata_dir = get_kdata_dir_csv(item, 'bfq')
    if not os.path.exists(bfq_kdata_dir):
        os.makedirs(bfq_kdata_dir)

    hfq_kdata_dir = get_kdata_dir_csv(item, 'hfq')
    if not os.path.exists(hfq_kdata_dir):
        os.makedirs(hfq_kdata_dir)


def init_env():
    if not os.path.exists(settings.FILES_STORE):
        os.makedirs(settings.FILES_STORE)
    for _, item in get_security_list().iterrows():
        mkdir_for_security(item)


@defer.inlineCallbacks
def crawl():
    # yield runner.crawl(SecurityListSpider)
    # yield runner.crawl(StockTradingDateSpider)
    # yield runner.crawl(StockKDataSpiderTHS)
    yield runner.crawl(StockKDataSpider)

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