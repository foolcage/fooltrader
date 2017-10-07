import argparse

from scrapy.crawler import CrawlerProcess

from fooltrader.spiders.security_list_spider import SecurityListSpider
from fooltrader.spiders.stock_kdata_spider import StockKDataSpider


def crawl(*spiders):
    process = CrawlerProcess()
    for spider in spiders:
        process.crawl(spider)
    process.start()


parser = argparse.ArgumentParser()

parser.add_argument("-s", "--stock_list", action="store_true", help="download the stock list")

parser.add_argument("-k", "--kdata", action="store_true", help="download the stock kdata")

args = parser.parse_args()

if args.stock_list:
    crawl(SecurityListSpider)

if args.stock_list:
    crawl(StockKDataSpider)
