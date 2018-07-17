# -*- coding: utf-8 -*-

import io
import os
from datetime import datetime

import pandas as pd
import scrapy
from scrapy import Request
from scrapy import signals

from fooltrader.api.technical import get_security_list
from fooltrader.contract.data_contract import KDATA_STOCK_COL, KDATA_COLUMN_163, KDATA_INDEX_COLUMN_163, \
    KDATA_INDEX_COL
from fooltrader.contract.files_contract import get_kdata_path
from fooltrader.settings import STOCK_START_CODE, STOCK_END_CODE
from fooltrader.spiders.common import random_proxy
from fooltrader.utils import utils


class StockKdata163Spider(scrapy.Spider):
    name = "stock_kdata_163"

    custom_settings = {
        # 'DOWNLOAD_DELAY': 2,
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 8,

        'SPIDER_MIDDLEWARES': {
            'fooltrader.middlewares.FoolErrorMiddleware': 1000,
        }
    }

    # 指定日期的话，是用来抓增量数据的
    # 如果需要代理请打开
    # @random_proxy
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
            for _, item in get_security_list(start_code=STOCK_START_CODE, end_code=STOCK_END_CODE).iterrows():
                for request in self.yield_request(item):
                    yield request

    def download_day_k_data(self, response):
        path = response.meta['path']
        item = response.meta['item']

        try:
            # 已经保存的csv数据
            if os.path.exists(path):
                saved_df = pd.read_csv(path, dtype=str)
            else:
                saved_df = pd.DataFrame()

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
                df.columns = KDATA_INDEX_COL
            # 股票数据
            else:
                df = df.loc[:,
                     ['日期', 'code', 'name', '最低价', '开盘价', '收盘价', '最高价', '成交量', '成交金额', 'securityId', '前收盘', '涨跌额',
                      '涨跌幅', '换手率', '总市值', '流通市值']]
                df['factor'] = None
                df.columns = KDATA_STOCK_COL

            # 合并到当前csv中
            saved_df = saved_df.append(df, ignore_index=True)

            if item['type'] == 'index':
                saved_df = saved_df.dropna(subset=KDATA_INDEX_COLUMN_163)
                # 保证col顺序
                saved_df = saved_df.loc[:, KDATA_INDEX_COL]
            else:
                saved_df = saved_df.dropna(subset=KDATA_COLUMN_163)
                # 保证col顺序
                saved_df = saved_df.loc[:, KDATA_STOCK_COL]

            saved_df = saved_df.drop_duplicates(subset='timestamp', keep='last')
            saved_df = saved_df.set_index(saved_df['timestamp'],drop=False)
            saved_df.index = pd.to_datetime(saved_df.index)
            saved_df = saved_df.sort_index()
            saved_df.to_csv(path, index=False)
        except Exception as e:
            self.logger.exception('error when getting k data url={} error={}'.format(response.url, e))

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(StockKdata163Spider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider, reason):
        spider.logger.info('Spider closed: %s,%s\n', spider.name, reason)

    def get_k_data_url(self, exchange, code, start, end):
        return 'http://quotes.money.163.com/service/chddata.html?code={}{}&start={}&end={}'.format(
            exchange, code, start, end)
