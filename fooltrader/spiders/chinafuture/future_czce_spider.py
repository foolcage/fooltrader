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


class FutureCzceSpider(scrapy.Spider):
    name = "future_czce_spider"

    custom_settings = {
        # 'DOWNLOAD_DELAY': 2,
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 8,

    }

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.trading_dates = None

    def start_requests(self):
        if self.dataType is None:
            today = pd.Timestamp.today()
            for date in pd.date_range(start=today.date()-pd.Timedelta(days=today.dayofyear-1),end=today):
                the_dir = get_exchange_cache_path(security_type='future',exchange='czce',the_date=to_timestamp(date),data_type='day_kdata')+'.xls'
                if(date.dayofweek<5 and not os.path.exists(the_dir)):
                    yield Request(url="http://www.czce.com.cn/portal/DFSStaticFiles/Future/"+date.strftime("%Y/%Y%m%d")+"/FutureDataDaily.xls",callback=self.download_czce_kline_data,meta={'filename':the_dir})
        elif self.dataType=='historyk':
            yield Request(url="http://www.czce.com.cn/portal/jysj/qhjysj/lshqxz/A09112017index_1.htm",callback=self.download_czce_history_data)
        elif self.dataType=='inventory':
            today = pd.Timestamp.today()
            for date in pd.date_range(start=today.date()-pd.Timedelta(weeks=450),end=today):
                the_dir = get_exchange_cache_path(security_type='future',exchange='czce',the_date=to_timestamp(date),data_type='inventory')+'.xls'
                if(date.dayofweek<5 and not os.path.exists(the_dir)):
                    yield Request(url="http://www.czce.com.cn/portal/DFSStaticFiles/Future/"+date.strftime("%Y/%Y%m%d")+"/FutureDataHolding.xls",callback=self.download_czce_kline_data,meta={'filename':the_dir})



    def download_czce_kline_data(self,response):
        content_type_header = response.headers.get('content-type', None)
        the_path = response.meta['filename']

        if content_type_header.decode("utf-8") == 'application/zip' or content_type_header.decode("utf-8") == 'text/csv' or content_type_header.decode("utf-8") == 'application/x-zip-compressed' or content_type_header.decode("utf-8") == 'application/excel':
            with open(the_path, "wb") as f:
                f.write(response.body)
                f.flush()

        else:
            self.logger.error(
                "get czce year  data failed:the_path={} url={} content type={} ".format(
                                                                                                 the_path,
                                                                                                 response.url,
                                                                                                 content_type_header))

    def download_czce_history_data(self,response):
        the_dir = get_exchange_cache_dir(security_type='future', exchange='czce')
        for filepath in response.xpath('//a[contains(@href,"zip")]').xpath('@href').extract():
            yield Request(url="http://www.czce.com.cn/"+filepath,
                      meta={'filename':os.path.join(the_dir,("" if filepath.split("/")[-2] == "exchange" else filepath.split("/")[-2]) +filepath.split("/")[-1])},
                      callback=self.download_czce_history_data_file)

    def download_czce_history_data_file(self,response):
        content_type_header = response.headers.get('content-type', None)
        the_path = response.meta['filename']

        if content_type_header.decode("utf-8") == 'application/zip' or content_type_header.decode("utf-8") == 'text/csv' or content_type_header.decode("utf-8") == 'application/x-zip-compressed':
            with open(the_path, "wb") as f:
                f.write(response.body)
                f.flush()

        else:
            self.logger.error(
                "get shfe year  data failed:the_path={} url={} content type={} ".format(
                                                                                                 the_path,
                                                                                                 response.url,
                                                                                                 content_type_header))
