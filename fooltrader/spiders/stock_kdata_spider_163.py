import io
from datetime import datetime

import pandas as pd
import scrapy
from scrapy import Request
from scrapy import signals

from fooltrader.api.quote import get_security_list
from fooltrader.contract.data_contract import KDATA_COLUMN_FULL
from fooltrader.contract.files_contract import get_kdata_path_163


class StockKdataSpider163(scrapy.Spider):
    name = "stock_kdata_163"

    custom_settings = {
        # 'DOWNLOAD_DELAY': 2,
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 8,

        'SPIDER_MIDDLEWARES': {
            'fooltrader.middlewares.FoolErrorMiddleware': 1000,
        }
    }

    def yield_request(self, item, trading_dates=[]):

        data_path = get_kdata_path_163(item)
        if trading_dates:
            start = trading_dates[0]
            end = trading_dates[-1]
        else:
            start = item['listDate'].replace('-', '')
            end = datetime.today().strftime('%Y%m%d')

        if item['exchange'] == 'sh':
            exchange_flag = 0
        else:
            exchange_flag = 1
        url = self.get_k_data_url(exchange_flag, item['code'], start, end)
        yield Request(url=url, meta={'path': data_path, 'item': item},
                      callback=self.download_day_k_data)

    def start_requests(self):
        item = self.settings.get("security_item")
        trading_dates = self.settings.get("trading_dates")
        if item is not None:
            for request in self.yield_request(item, trading_dates):
                yield request
        else:
            for _, item in get_security_list().iterrows():
                for request in self.yield_request(item):
                    yield request

    def download_day_k_data(self, response):
        path = response.meta['path']
        item = response.meta['item']

        try:
            df = pd.read_csv(io.BytesIO(response.body), encoding='GB2312', na_values='None')
            df['code'] = item['code']
            df['securityId'] = item['id']
            df = df.loc[:,
                 ['日期', 'code', '最低价', '开盘价', '收盘价', '最高价', '成交量', '成交金额', 'securityId', '前收盘', '涨跌额', '涨跌幅', '换手率',
                  '总市值', '流通市值']]
            df.dropna()
            df.columns = KDATA_COLUMN_FULL
            df = df.set_index(df['timestamp'])
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            df.to_csv(path, index=False)
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
