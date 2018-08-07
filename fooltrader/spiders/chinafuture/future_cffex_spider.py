# -*- coding: utf-8 -*-

import os
from datetime import datetime

import scrapy
from scrapy import Request
from scrapy import signals
import pandas as pd

from fooltrader.api.technical import parse_shfe_data, parse_shfe_day_data
from fooltrader.contract.files_contract import get_exchange_cache_dir, get_exchange_cache_path
from fooltrader.utils.utils import to_timestamp


class FutureCffexSpider(scrapy.Spider):
    name = "future_cffex_spider"

    custom_settings = {
        # 'DOWNLOAD_DELAY': 2,
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 8,

    }

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.trading_dates = None

    def start_requests(self):
        if self.dataType is None or self.dataType=='dayk':
            daterange=pd.date_range(start='2006-06-30',end=pd.Timestamp.today())
            daterange=daterange[daterange.dayofweek<5]
            for i in daterange:
                the_dir = get_exchange_cache_path(security_type='future',exchange='cffex',data_type='day_kdata',the_date=to_timestamp(i))+".csv"
                if not os.path.exists(the_dir):
                    yield Request(url="http://www.cffex.com.cn/sj/hqsj/rtj/"+i.strftime("%Y%m/%d/%Y%m%d")+"_1.csv",callback=self.download_cffex_history_data_file,meta={'filename':the_dir})
        elif self.dataType =='inventory':
            daterange=pd.date_range(start='2006-06-30',end=pd.Timestamp.today())
            k=['IF','IC','IH','T','TF']
            daterange=daterange[daterange.dayofweek<5]
            for i in daterange:
                for j in k:
                    the_dir = get_exchange_cache_path(security_type='future',exchange='cffex',data_type='inventory',the_date=to_timestamp(i))+j+".csv"
                    if not os.path.exists(the_dir):
                        yield Request(url="http://www.cffex.com.cn/sj/ccpm/"+i.strftime("%Y%m/%d/")+j+"_1.csv",callback=self.download_cffex_history_data_file,meta={'filename':the_dir})




    def download_cffex_history_data_file(self,response):
        content_type_header = response.headers.get('content-type', None)
        the_path = response.meta['filename']

        if content_type_header.decode("utf-8") == 'application/zip' or content_type_header.decode("utf-8") == 'text/csv':
            with open(the_path, "wb") as f:
                f.write(response.body)
                f.flush()

        else:
            self.logger.error(
                "get cffex year  data failed:the_path={} url={} content type={} ".format(
                                                                                                 the_path,
                                                                                                 response.url,
                                                                                                 content_type_header))
