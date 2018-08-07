# -*- coding: utf-8 -*-

import io
import os

import pandas as pd
import scrapy
from scrapy import Request
from scrapy import signals

from fooltrader.contract import files_contract
from fooltrader.contract.data_contract import STOCK_META_COL
from fooltrader.utils.utils import to_time_str


class AmericaListSpider(scrapy.Spider):
    name = "stock_list"

    def start_requests(self):
        yield Request(
            url='http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nasdaq&render=download',
            meta={'exchange': 'nasdaq'},
            callback=self.download_stock_list)

        yield Request(
            url='http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nyse&render=download',
            meta={'exchange': 'nyse'},
            callback=self.download_stock_list)

        yield Request(
            url='http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=amex&render=download',
            meta={'exchange': 'amex'},
            callback=self.download_stock_list)

    def download_stock_list(self, response):
        exchange = response.meta['exchange']
        path = files_contract.get_security_list_path('stock', exchange)
        df = pd.read_csv(io.BytesIO(response.body), dtype=str)
        if df is not None:
            if os.path.exists(path):
                df_current = pd.read_csv(path, dtype=str)
                df_current = df_current.set_index('code', drop=False)
            else:
                df_current = pd.DataFrame()

            df = df.loc[:, ['Symbol', 'Name', 'IPOyear', 'Sector', 'industry']]
            df = df.dropna(subset=['Symbol', 'Name'])
            df.columns = ['code', 'name', 'listDate', 'sector', 'industry']
            df.listDate = df.listDate.apply(lambda x: to_time_str(x))
            df['exchange'] = exchange
            df['type'] = 'stock'
            df['id'] = df[['type', 'exchange', 'code']].apply(lambda x: '_'.join(x.astype(str)), axis=1)
            df['sinaIndustry'] = ''
            df['sinaConcept'] = ''
            df['sinaArea'] = ''
            df['timestamp'] = df['listDate']
            df = df.set_index('code', drop=False)

            diff = set(df.index.tolist()) - set(df_current.index.tolist())
            diff = [item for item in diff if item != 'nan']

            if diff:
                df_current = df_current.append(df.loc[diff, :], ignore_index=False)
                df_current = df_current.loc[:, STOCK_META_COL]
                df_current.columns = STOCK_META_COL
                df_current.to_csv(path, index=False)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(AmericaListSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider, reason):
        spider.logger.info('Spider closed: %s,%s\n', spider.name, reason)
