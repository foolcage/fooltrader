# -*- coding: utf-8 -*-

import json
from datetime import datetime

import pandas as pd
import scrapy
from scrapy import Request
from scrapy import signals

from fooltrader.api.technical import get_trading_calendar
from fooltrader.contract.files_contract import get_exchange_trading_calendar_path
from fooltrader.utils.utils import next_date, to_time_str, drop_duplicate


class ShfeTradingCalendarSpider(scrapy.Spider):
    name = "shfe_trading_calendar_spider"

    custom_settings = {
        # 'DOWNLOAD_DELAY': 2,
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 8,

        # 'SPIDER_MIDDLEWARES': {
        #     'fooltrader.middlewares.FoolErrorMiddleware': 1000,
        # }
    }

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        # python list  thread safe,no need lock
        self.saved_trading_dates = get_trading_calendar(security_type='future', exchange='shfe')
        self.trading_dates = []

    def start_requests(self):
        # 往年的统计数据可以直接下载，只从今年开始
        latest_trading_date = "{}0101".format(datetime.today().year)

        # 检查已经保存的
        if self.saved_trading_dates:
            latest_trading_date = self.saved_trading_dates[-1]
            latest_trading_date = next_date(latest_trading_date)

        for the_date in pd.date_range(start=latest_trading_date, end=datetime.today()):
            # 双休
            if the_date.weekday() == 5 or the_date.weekday() == 6:
                continue
            the_date_str = to_time_str(the_time=the_date, time_fmt='%Y%m%d')
            yield Request(url=self.get_trading_date_url(the_date=the_date_str),
                          meta={'the_date': the_date_str},
                          callback=self.download_trading_calendar)

    def download_trading_calendar(self, response):
        if response.status == 200:
            self.trading_dates.append(response.meta['the_date'])

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(ShfeTradingCalendarSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider, reason):
        if self.trading_dates:
            if self.saved_trading_dates:
                self.trading_dates.append(self.saved_trading_dates)
            result_list = drop_duplicate(self.trading_dates)
            result_list = sorted(result_list)

            the_path = get_exchange_trading_calendar_path('future', 'shfe')
            with open(the_path, 'w') as outfile:
                json.dump(result_list, outfile)

        spider.logger.info('Spider closed: %s,%s\n', spider.name, reason)

    def get_trading_date_url(self, the_date):
        return "http://www.shfe.com.cn/bourseService/businessdata/calendar/{}all.dat".format(the_date)
