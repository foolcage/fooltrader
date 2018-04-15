# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime

import pandas as pd
import scrapy
from scrapy import Request
from scrapy import signals

from fooltrader.api.quote import parse_shfe_data
from fooltrader.contract.files_contract import get_exchange_cache_dir
from fooltrader.utils.utils import to_time_str


class FutureShfeSpider(scrapy.Spider):
    name = "future_shfe_spider"

    custom_settings = {
        # 'DOWNLOAD_DELAY': 2,
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 8,

    }

    def start_requests(self):
        start_date = self.settings.get("start_date")
        end_date = self.settings.get("end_date")
        if start_date and end_date:
            for the_date in pd.date_range(start_date, end_date):
                yield Request(url=self.get_k_data_url(the_date=the_date),
                              meta={'the_date': to_time_str(the_time=the_date, time_fmt='%Y%m%d')},
                              callback=self.download_shfe_data_by_date)
        else:
            # 直接抓年度统计数据
            for the_year in range(2009, datetime.today().year):
                the_dir = get_exchange_cache_dir(security_type='future', exchange='shfe')
                the_path = os.path.join(the_dir, "{}_shfe_history_data.zip".format(the_year))

                if not os.path.exists(the_path):
                    yield Request(url=self.get_k_data_url(the_year=the_year),
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
            self.logger.error(
                "get shfe year {} data failed:the_path={} url={} content type={} body={}".format(the_year,
                                                                                                 the_path,
                                                                                                 response.url,
                                                                                                 content_type_header,
                                                                                                 response.body))

    def download_shfe_data_by_date(self, response):
        path = response.meta['path']
        the_date = response.meta['the_date']

        tmp_str = response.body.decode('UTF8')
        the_json = json.loads(tmp_str)
        the_datas = the_json['o_curinstrument']
        {'CLOSEPRICE': 11480,
         'DELIVERYMONTH': '1809',
         'HIGHESTPRICE': 11555,
         'LOWESTPRICE': 11320,
         'OPENINTEREST': 425692,
         'OPENINTERESTCHG': 3918,
         'OPENPRICE': 11495,
         'ORDERNO': 0,
         'PRESETTLEMENTPRICE': 11545,
         'PRODUCTID': 'ru_f    ',
         'PRODUCTNAME': '天然橡胶            ',
         'PRODUCTSORTNO': 100,
         'SETTLEMENTPRICE': 11465,
         'VOLUME': 456574,
         'ZD1_CHG': -65,
         'ZD2_CHG': -80}

        print(the_datas)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(FutureShfeSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider, reason):
        parse_shfe_data()
        spider.logger.info('Spider closed: %s,%s\n', spider.name, reason)

    def get_k_data_url(self, the_date=None, the_year=2009):
        if the_year:
            return 'http://www.shfe.com.cn/historyData/MarketData_Year_{}.zip'.format(the_year)
        elif the_date:
            return 'http://www.shfe.com.cn/data/dailydata/kx/kx{}.dat'.format(the_date)

    def get_trading_date_url(self):
        return 'http://www.shfe.com.cn/bourseService/businessdata/calendar/20171201all.dat'
