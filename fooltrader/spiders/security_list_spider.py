# -*- coding: utf-8 -*-

import io
import os

import pandas as pd
import scrapy
from kafka import KafkaProducer
from scrapy import Request
from scrapy import signals

from fooltrader.consts import DEFAULT_SH_HEADER, DEFAULT_SZ_HEADER
from fooltrader.contract import files_contract
from fooltrader.contract.data_contract import STOCK_META_COL
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
        df = None
        if exchange == 'sh':
            df = pd.read_csv(io.BytesIO(response.body), sep='\s+', encoding='GB2312', dtype=str)
        elif exchange == 'sz':
            df = pd.read_excel(io.BytesIO(response.body), sheet_name='上市公司列表', dtype=str)
        if df is not None:
            if os.path.exists(path):
                df_current = pd.read_csv(path, dtype=str)
                df_current = df_current.set_index('code', drop=False)
            else:
                df_current = pd.DataFrame()

            df = df.loc[:, ['A股代码', 'A股简称', 'A股上市日期']]
            df.columns = ['code', 'name', 'listDate']
            df['exchange'] = exchange
            df['type'] = 'stock'
            df['id'] = df[['type', 'exchange', 'code']].apply(lambda x: '_'.join(x.astype(str)), axis=1)
            df = df.dropna(axis=0, how='any')
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
        spider = super(SecurityListSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider, reason):
        spider.logger.info('Spider closed: %s,%s\n', spider.name, reason)
