# -*- coding: utf-8 -*-

import os
from datetime import datetime
import pandas as pd

import scrapy
from scrapy import Request
from scrapy import signals

from fooltrader.api.technical import parse_shfe_data, parse_shfe_day_data
from fooltrader.contract.files_contract import get_exchange_cache_dir, get_exchange_cache_path
from fooltrader.utils.utils import to_timestamp


class FutureShfeSpider(scrapy.Spider):
    name = "future_shfe_spider"

    custom_settings = {
        # 'DOWNLOAD_DELAY': 2,
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 8,

    }

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.trading_dates = None

    def start_requests(self):
        self.trading_dates = self.settings.get("trading_dates")
        if self.dataType or self.dataType=='inventory':
            today = pd.Timestamp.today()
            for date in pd.date_range(start=today.date()-pd.Timedelta(weeks=520),end=today):
                the_dir=get_exchange_cache_path(security_type='future',exchange='shfe',the_date=to_timestamp(date),data_type='inventory')+'.json'
                if date.dayofweek<5 and not os.path.exists(the_dir):
                    yield Request(url=self.get_day_inventory_url(the_date=date.strftime('%Y%m%d')),
                              meta={'the_date': date,
                                    'the_path': the_dir},
                              callback=self.download_shfe_data_by_date)

        if self.trading_dates:
            # 每天的数据
            for the_date in self.trading_dates:
                the_path = get_exchange_cache_path(security_type='future', exchange='shfe',
                                                   the_date=to_timestamp(the_date),
                                                   data_type='day_kdata')

                yield Request(url=self.get_day_kdata_url(the_date=the_date),
                              meta={'the_date': the_date,
                                    'the_path': the_path},
                              callback=self.download_shfe_data_by_date)
        else:
            # 直接抓年度统计数据
            for the_year in range(2009, datetime.today().year):
                the_dir = get_exchange_cache_dir(security_type='future', exchange='shfe')
                the_path = os.path.join(the_dir, "{}_shfe_history_data.zip".format(the_year))

                if not os.path.exists(the_path):
                    yield Request(url=self.get_year_k_data_url(the_year=the_year),
                                  meta={'the_year': the_year,
                                        'the_path': the_path},
                                  callback=self.download_shfe_history_data)

    def download_shfe_history_data(self, response):
        content_type_header = response.headers.get('content-type', None)
        the_year = response.meta['the_year']
        the_path = response.meta['the_path']

        if content_type_header.decode("utf-8") == 'application/zip':
            with open(the_path, "wb") as f:
                f.write(response.body)
                f.flush()

        else:
            self.logger.exception(
                "get shfe year {} data failed:the_path={} url={} content type={} body={}".format(the_year,
                                                                                                 the_path,
                                                                                                 response.url,
                                                                                                 content_type_header,
                                                                                                 response.body))

    def download_shfe_data_by_date(self, response):
        the_path = response.meta['the_path']

        # 缓存数据
        with open(the_path, "wb") as f:
            f.write(response.body)
            f.flush()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(FutureShfeSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider, reason):
        if self.trading_dates:
            parse_shfe_day_data()
        else:
            parse_shfe_data()
        spider.logger.info('Spider closed: %s,%s\n', spider.name, reason)

    def get_year_k_data_url(self, the_year):
        return 'http://www.shfe.com.cn/historyData/MarketData_Year_{}.zip'.format(the_year)

    def get_day_kdata_url(self, the_date):
        return 'http://www.shfe.com.cn/data/dailydata/kx/kx{}.dat'.format(the_date)

    def get_day_inventory_url(self, the_date):
        return 'http://www.shfe.com.cn/data/dailydata/kx/pm{}.dat'.format(the_date)

    def get_trading_date_url(self):
        return 'http://www.shfe.com.cn/bourseService/businessdata/calendar/20171201all.dat'
