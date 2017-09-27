from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from twisted.internet import defer
from twisted.internet import reactor

from fooltrader.proxy.proxy_manager import int_proxy
from fooltrader.spiders.proxy_spider import ProxySpider
from fooltrader.spiders.security_list_spider import SecurityListSpider
from fooltrader.spiders.stock_finance_spider import StockFinanceSpider
from fooltrader.spiders.stock_forecast_spider import StockForecastSpider
from fooltrader.spiders.stock_kdata_spider import StockKDataSpider
from fooltrader.spiders.stock_tick_spider import StockTickSpider
from fooltrader.utils.utils import setup_env

configure_logging()

setup_env()

int_proxy()

runner = CrawlerRunner()


@defer.inlineCallbacks
def crawl():
    # yield runner.crawl(SecurityListSpider)
    # yield runner.crawl(StockKDataSpider)

    yield runner.crawl(StockTickSpider)
    # yield runner.crawl(StockFinanceSpider)
    # yield runner.crawl(StockGNSpider)
    # yield runner.crawl(StockForecastSpider)
    # yield runner.crawl(ProxySpider)

    reactor.stop()


crawl()

reactor.run()  # the script will block here until the last crawl call is finished
