import io

import pandas as pd
import scrapy
from kafka import KafkaProducer
from scrapy import Request
from scrapy import signals

from fooltrader.consts import DEFAULT_SH_HEADER, DEFAULT_SZ_HEADER
from fooltrader.contract import files_contract
from fooltrader.settings import KAFKA_HOST, AUTO_KAFKA


# TODO:check whether has new stock and new trading date to ignore download again
class SecurityListSpider(scrapy.Spider):
    name = "stock_list"

    if AUTO_KAFKA:
        producer = KafkaProducer(bootstrap_servers=KAFKA_HOST)

    def start_requests(self):
        yield Request(
            url='http://query.sse.com.cn/security/stock/downloadStockListFile.do?csrcCode=&stockCode=&areaName=&stockType=1',
            headers=DEFAULT_SH_HEADER,
            meta={'exchange': 'sh'},
            callback=self.download_stock_list)

        yield Request(
            url='http://www.szse.cn/szseWeb/ShowReport.szse?SHOWTYPE=xlsx&CATALOGID=1110&tab1PAGENUM=1&ENCODE=1&TABKEY=tab1',
            headers=DEFAULT_SZ_HEADER,
            meta={'exchange': 'sz'},
            callback=self.download_stock_list)

    def download_stock_list(self, response):
        exchange = response.meta['exchange']
        path = files_contract.get_security_list_path('stock', exchange)
        if exchange == 'sh':
            df = pd.read_csv(io.BytesIO(response.body), sep='\s+', encoding='GB2312')
            df = df.loc[:, ['A股代码', 'A股简称', 'A股上市日期']]
            df.columns = ['code', 'name', 'listDate']
            df['exchange'] = exchange
            df['type'] = 'stock'
            df['id'] = df[['type', 'exchange', 'code']].apply(lambda x: '_'.join(x.astype(str)), axis=1)
            df.to_csv(path, index=False)
        elif exchange == 'sz':
            df = pd.read_excel(io.BytesIO(response.body), sheet_name='上市公司列表', parse_dates=['A股上市日期'],
                               converters={'A股代码': str})
            df = df.loc[:, ['A股代码', 'A股上市日期', 'A股简称']]
            df.columns = ['code', 'name', 'listDate']
            df['exchange'] = exchange
            df['type'] = 'stock'
            df['id'] = df[['type', 'exchange', 'code']].apply(lambda x: '_'.join(x.astype(str)), axis=1)
            df.to_csv(path, index=False)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(SecurityListSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider, reason):
        spider.logger.info('Spider closed: %s,%s\n', spider.name, reason)
