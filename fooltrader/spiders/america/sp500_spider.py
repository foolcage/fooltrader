# -*- coding: utf-8 -*-

import pandas as pd
import scrapy
from scrapy import Request
from scrapy import Selector
from scrapy import signals

from fooltrader.contract.files_contract import get_kdata_path
from fooltrader.utils.utils import index_df_with_time, to_time_str, to_float


class Sp500Spider(scrapy.Spider):
    name = "sp500_spider"

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.security_item = {'id': 'index_nasdaq_sp500',
                              'code': 'SP500',
                              'name': 'SP500',
                              'listDate': '1871-01-01',
                              'timestamp': '1871-01-01',
                              'exchange': 'nasdaq',
                              'type': 'index'}
        self.df_close = pd.DataFrame()
        self.df_pe = pd.DataFrame()

    def start_requests(self):
        pe_url = 'http://www.multpl.com/table?f=m'
        price_url = 'http://www.multpl.com/s-p-500-historical-prices/table/by-month'

        yield Request(url=pe_url,
                      callback=self.download_sp500_pe)

        yield Request(url=price_url,
                      callback=self.download_sp500_price)

    def download_sp500_price(self, response):
        trs = response.xpath('//*[@id="datatable"]/tr').extract()

        price_jsons = []

        try:
            for tr in trs[1:]:
                tds = Selector(text=tr).xpath('//td//text()').extract()
                tds = [x.strip() for x in tds if x.strip()]

                price_jsons.append({"timestamp": to_time_str(tds[0]),
                                    "close": to_float(tds[1])})

            if price_jsons:
                self.df_close = self.df_close.append(price_jsons, ignore_index=True)
                self.df_close = index_df_with_time(self.df_close)
        except Exception as e:
            self.logger.exception('error when getting sp500 price url={} error={}'.format(response.url, e))

    def download_sp500_pe(self, response):
        trs = response.xpath('//*[@id="datatable"]/tr').extract()

        price_jsons = []

        try:
            for tr in trs[1:]:
                tds = Selector(text=tr).xpath('//td//text()').extract()
                tds = [x.strip() for x in tds if x.strip()]

                price_jsons.append({"timestamp": to_time_str(tds[0]),
                                    "pe": to_float(tds[1])})

            if price_jsons:
                self.df_pe = self.df_pe.append(price_jsons, ignore_index=True)
                self.df_pe = index_df_with_time(self.df_pe)
        except Exception as e:
            self.logger.exception('error when getting sp500 pe url={} error={}'.format(response.url, e))

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(Sp500Spider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider, reason):
        self.df_pe['close'] = self.df_close['close']
        self.df_pe['code'] = self.security_item['code']
        self.df_pe['securityId'] = self.security_item['id']
        self.df_pe['name'] = self.security_item['name']
        self.df_pe.to_csv(get_kdata_path(self.security_item), index=False)
        spider.logger.info('Spider closed: %s,%s\n', spider.name, reason)
