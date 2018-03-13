# -*- coding: utf-8 -*-

import io
import os
from datetime import datetime

import pandas as pd
import scrapy
from scrapy import Request
from scrapy import signals

from fooltrader.api.quote import get_security_list
from fooltrader.contract.data_contract import KDATA_COLUMN_STOCK, KDATA_COLUMN_163, KDATA_INDEX_COLUMN_163, \
    KDATA_COLUMN_INDEX
from fooltrader.contract.files_contract import get_kdata_path
from fooltrader.utils import utils


class StockKdataSpider163(scrapy.Spider):
    name = "stock_kdata_163"

    custom_settings = {
        # 'DOWNLOAD_DELAY': 2,
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 8,

        'SPIDER_MIDDLEWARES': {
            'fooltrader.middlewares.FoolErrorMiddleware': 1000,
        }
    }

    # 指定日期的话，是用来抓增量数据的
    def yield_request(self, item, start_date=None, end_date=None):
        data_path = get_kdata_path(item, source='163')

        if start_date:
            start = start_date.strftime('%Y%m%d')
        else:
            start = item['listDate'].replace('-', '')

        if end_date:
            end = end_date.strftime('%Y%m%d')
        else:
            end = datetime.today().strftime('%Y%m%d')

        if not os.path.exists(data_path) or start_date or end_date:
            if item['exchange'] == 'sh':
                exchange_flag = 0
            else:
                exchange_flag = 1
            url = self.get_k_data_url(exchange_flag, item['code'], start, end)
            yield Request(url=url, meta={'path': data_path, 'item': item},
                          callback=self.download_day_k_data)

    def start_requests(self):
        item = self.settings.get("security_item")
        start_date = self.settings.get("start_date")
        end_date = self.settings.get("end_date")
        if item is not None:
            for request in self.yield_request(item, start_date, end_date):
                yield request
        else:
            for _, item in get_security_list().iterrows():
                for request in self.yield_request(item):
                    yield request

    def download_day_k_data(self, response):
        path = response.meta['path']
        item = response.meta['item']

        try:
            # 已经保存的csv数据
            if os.path.exists(path):
                df_current = pd.read_csv(path, dtype=str)
                # 补全历史数据
                if 'name' not in df_current.columns:
                    df_current['name'] = item['name']
            else:
                df_current = pd.DataFrame()

            df = utils.read_csv(io.BytesIO(response.body), encoding='GB2312', na_values='None')
            df['code'] = item['code']
            df['securityId'] = item['id']
            df['name'] = item['name']
            # 指数数据
            if item['type'] == 'index':
                df = df.loc[:,
                     ['日期', 'code', 'name', '最低价', '开盘价', '收盘价', '最高价', '成交量', '成交金额', 'securityId', '前收盘', '涨跌额',
                      '涨跌幅']]
                df['turnoverRate'] = None
                df['tCap'] = None
                df['mCap'] = None
                df['pe'] = None
                df.columns = KDATA_COLUMN_INDEX
            # 股票数据
            else:
                df = df.loc[:,
                     ['日期', 'code', 'name', '最低价', '开盘价', '收盘价', '最高价', '成交量', '成交金额', 'securityId', '前收盘', '涨跌额',
                      '涨跌幅', '换手率', '总市值', '流通市值']]
                df['factor'] = None
                df.columns = KDATA_COLUMN_STOCK

            # 合并到当前csv中
            df_current = df_current.append(df, ignore_index=True)

            if item['type'] == 'index':
                df_current = df_current.dropna(subset=KDATA_INDEX_COLUMN_163)
                # 保证col顺序
                df_current = df_current.loc[:, KDATA_COLUMN_INDEX]
            else:
                df_current = df_current.dropna(subset=KDATA_COLUMN_163)
                # 保证col顺序
                df_current = df_current.loc[:, KDATA_COLUMN_STOCK]

            df_current = df_current.drop_duplicates(subset='timestamp', keep='last')
            df_current = df_current.set_index(df_current['timestamp'],drop=False)
            df_current.index = pd.to_datetime(df_current.index)
            df_current = df_current.sort_index()
            df_current.to_csv(path, index=False)
        except Exception as e:
            self.logger.error('error when getting k data url={} error={}'.format(response.url, e))

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(StockKdataSpider163, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider, reason):
        spider.logger.info('Spider closed: %s,%s\n', spider.name, reason)

    def get_k_data_url(self, exchange, code, start, end):
        return 'http://quotes.money.163.com/service/chddata.html?code={}{}&start={}&end={}'.format(
            exchange, code, start, end)
