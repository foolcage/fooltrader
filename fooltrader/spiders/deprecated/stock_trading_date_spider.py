# -*- coding: utf-8 -*-

import json
from datetime import datetime

import scrapy
from scrapy import Request
from scrapy import signals

from fooltrader.api.technical import get_security_list
from fooltrader.consts import SSE_KDATA_HEADER
from fooltrader.contract.files_contract import get_trading_dates_path_sse
from fooltrader.settings import TIME_FORMAT_DAY, STOCK_START_CODE, STOCK_END_CODE


# 本来想以交易所网站的数据为标准,结果发现数据质量堪忧，比如很多股票的交易日跑到周末去了，上市前也有数据
# 所以:不要用这个爬虫
class StockTradingDateSpider(scrapy.Spider):
    name = "stock_trading_date"

    custom_settings = {
        # 'DOWNLOAD_DELAY': 2,
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 8,

        'SPIDER_MIDDLEWARES': {
            'fooltrader.middlewares.FoolErrorMiddleware': 1000,
        }
    }

    def yield_request(self, item):

        data_path = get_trading_dates_path_sse(item)  # get day k data
        url = self.get_k_data_url(item['exchange'], item['code'])
        yield Request(url=url, headers=SSE_KDATA_HEADER,
                      meta={'path': data_path, 'item': item},
                      callback=self.download_day_k_data)

    def start_requests(self):
        item = self.settings.get("security_item")
        if item is not None:
            for request in self.yield_request(item):
                yield request
        else:
            for _, item in get_security_list(start_code=STOCK_START_CODE, end_code=STOCK_END_CODE).iterrows():
                for request in self.yield_request(item):
                    yield request

    def download_day_k_data(self, response):
        path = response.meta['path']
        item = response.meta['item']

        trading_dates = []

        try:
            tmp_str = response.text
            json_str = tmp_str[tmp_str.index('{'):tmp_str.index('}') + 1]
            tmp_json = json.loads(json_str)

            # parse the trading dates
            dates = [items[0] for items in tmp_json['kline']]
            trading_dates = [datetime.strptime(str(the_date), '%Y%m%d').strftime(TIME_FORMAT_DAY) for the_date in dates]


        except Exception as e:
            self.logger.exception('error when getting k data url={} error={}'.format(response.url, e))

        if len(trading_dates) > 0:
            try:
                with open(get_trading_dates_path_sse(item), "w") as f:
                    json.dump(trading_dates, f)
            except Exception as e:
                self.logger.exception(
                    'error when saving trading dates url={} path={} error={}'.format(response.url, path, e))

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(StockTradingDateSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider, reason):
        spider.logger.info('Spider closed: %s,%s\n', spider.name, reason)

    def get_k_data_url(self, exchange, code):
        return 'http://yunhq.sse.com.cn:32041/v1/{}1/dayk/{}?callback=jQuery111202351405749576012_1507560840520&select=date&begin=0&end=10000&_=1507560840536'.format(
            exchange, code)
