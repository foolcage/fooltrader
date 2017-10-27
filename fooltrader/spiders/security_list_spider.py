import json

import scrapy
from kafka import KafkaProducer
from scrapy import Request
from scrapy import signals

from fooltrader.consts import DEFAULT_SH_HEADER, DEFAULT_SZ_HEADER
from fooltrader.settings import KAFKA_HOST, AUTO_KAFKA
from fooltrader.utils.utils import get_sh_stock_list_path, get_sz_stock_list_path, get_security_item


# TODO:check whether has new stock and new trading date to ignore download again
class SecurityListSpider(scrapy.Spider):
    name = "stock_list"

    if AUTO_KAFKA:
        producer = KafkaProducer(bootstrap_servers=KAFKA_HOST)

    def start_requests(self):
        yield Request(
            url='http://query.sse.com.cn/security/stock/downloadStockListFile.do?csrcCode=&stockCode=&areaName=&stockType=1',
            headers=DEFAULT_SH_HEADER,
            meta={'path': get_sh_stock_list_path(),
                  'exchange': 'sh'},
            callback=self.download_stock_list)

        yield Request(
            url='http://www.szse.cn/szseWeb/ShowReport.szse?SHOWTYPE=xlsx&CATALOGID=1110&tab1PAGENUM=1&ENCODE=1&TABKEY=tab1',
            headers=DEFAULT_SZ_HEADER,
            meta={'path': get_sz_stock_list_path(),
                  'exchange': 'sz'},
            callback=self.download_stock_list)

    def download_stock_list(self, response):
        path = response.meta['path']
        exchange = response.meta['exchange']
        with open(path, "wb") as f:
            f.write(response.body)
            if AUTO_KAFKA:
                for item in get_security_item(exchange):
                    self.producer.send('CHINA_STOCK', bytes(json.dumps(item, ensure_ascii=False), encoding='utf8'))

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(SecurityListSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider, reason):
        spider.logger.info('Spider closed: %s,%s\n', spider.name, reason)
