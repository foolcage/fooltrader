# -*- coding: utf-8 -*-

import io
import os

import scrapy
from scrapy import Request
from scrapy import signals

from fooltrader import settings
from fooltrader.api.technical import get_security_list, get_trading_dates, get_kdata
from fooltrader.consts import DEFAULT_TICK_HEADER
from fooltrader.contract.files_contract import get_tick_path
from fooltrader.settings import STOCK_START_CODE, STOCK_END_CODE
from fooltrader.utils.utils import get_datetime, kdata_to_tick, sina_tick_to_csv


class StockTickSpider(scrapy.Spider):
    name = "stock_tick"

    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 6,

        'SPIDER_MIDDLEWARES': {
            'fooltrader.middlewares.FoolErrorMiddleware': 1000,
        }
    }

    def yield_request(self, item, trading_dates=None):
        if not trading_dates:
            trading_dates = get_trading_dates(item)

        for trading_date in trading_dates:
            if get_datetime(trading_date) < get_datetime(settings.START_TICK_DATE) or get_datetime(
                    trading_date) < get_datetime(settings.AVAILABLE_TICK_DATE):
                continue
            path = get_tick_path(item, trading_date)

            if os.path.exists(path):
                continue
            yield Request(url=self.get_tick_url(trading_date, item['exchange'] + item['code']),
                          meta={'proxy': None,
                                'path': path,
                                'trading_date': trading_date,
                                'item': item},
                          headers=DEFAULT_TICK_HEADER,
                          callback=self.download_tick)

    def start_requests(self):
        item = self.settings.get("security_item")
        trading_dates = self.settings.get("trading_dates")
        if item is not None:
            for request in self.yield_request(item, trading_dates):
                yield request
        else:
            for _, item in get_security_list(start_code=STOCK_START_CODE, end_code=STOCK_END_CODE).iterrows():
                for request in self.yield_request(item):
                    yield request

    def download_tick(self, response):
        content_type_header = response.headers.get('content-type', None)
        if content_type_header.decode("utf-8") == 'application/vnd.ms-excel' or "当天没有数据" in response.body.decode(
                'GB2312'):
            trading_date = response.meta['trading_date']
            security_item = response.meta['item']
            if content_type_header.decode("utf-8") == 'application/vnd.ms-excel':
                content = response.body
            else:
                kdata_df = get_kdata(security_item, the_date=trading_date)
                if trading_date in kdata_df.index:
                    json_data = kdata_df.loc[trading_date, :]
                    content = kdata_to_tick(json_data)
                    self.logger.info(
                        "{} {} generate tick from kdata {}".format(security_item['code'], trading_date, content))
                    content = content.encode('GB2312')
            sina_tick_to_csv(security_item, io.BytesIO(content), trading_date)
        else:
            self.logger.exception(
                "get tick error:url={} content type={} body={}".format(response.url, content_type_header,
                                                                       response.body))

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(StockTickSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider, reason):
        spider.logger.info('Spider closed: %s,%s\n', spider.name, reason)

    def get_tick_url(self, date, code):
        return 'http://market.finance.sina.com.cn/downxls.php?date={}&symbol={}'.format(date, code)
