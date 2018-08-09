# -*- coding: utf-8 -*-

import os
from datetime import datetime
import pandas as pd

import scrapy
from scrapy import Request,FormRequest
from scrapy import signals

from fooltrader.api.technical import parse_shfe_data, parse_shfe_day_data
from fooltrader.contract.files_contract import get_exchange_cache_dir, get_exchange_cache_path
from fooltrader.utils.utils import to_timestamp


class FutureDceSpider(scrapy.Spider):
    name = "future_dce_spider"

    custom_settings = {
        # 'DOWNLOAD_DELAY': 2,
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 8,

    }

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)

    def start_requests(self):
        if self.dataType is None:
            return self.request_currentyear_kdata()
        elif self.dataType == 'historyk':
            return self.request_history_kdata()
        elif self.dataType == 'inventory':
            return self.request_inventory_data()
        else:
            return self.request_currentyear_kdata()

    def request_inventory_data(self):
        today = pd.Timestamp.today()
        requests = []
        for date in pd.date_range(start=today.date()-pd.Timedelta(weeks=520),end=today):
            the_dir = get_exchange_cache_path(security_type='future', exchange='dce',the_date=to_timestamp(date),data_type="day_inventory")+'.zip'
            if(date.dayofweek<5 and not os.path.exists(the_dir)):
                requests.append(FormRequest(url="http://www.dce.com.cn/publicweb/quotesdata/exportMemberDealPosiQuotesBatchData.html",formdata={
            'batchExportFlag':'batch',
            'contract.contract_id':'all',
            'contract.variety_id':'a',
            'year':str(date.year),
                'month':str(date.month-1),
                'day':str(date.day),
                'memberDealPosiQuotes.trade_type':'0',
                'memberDealPosiQuotes.variety':'all'
            },callback=self.download_dce_kline_data,meta={
                'filename':the_dir
            }))
        return requests

    def request_currentyear_kdata(self):
        today = pd.Timestamp.today()
        requests=[]
        for date in pd.date_range(start=today.date()-pd.Timedelta(days=today.dayofyear-1),end=today):
            the_dir = get_exchange_cache_path(security_type='future', exchange='dce',the_date=to_timestamp(date),data_type="day_kdata")+'.xls'
            if(date.dayofweek<5 and not os.path.exists(the_dir)):
                requests.append( FormRequest(url="http://www.dce.com.cn/publicweb/quotesdata/exportDayQuotesChData.html",formdata={
            'year':str(date.year),
                'month':str(date.month-1),
                'day':str(date.day),
                'dayQuotes.trade_type':'0',
                'dayQuotes.variety':'all',
                'exportType':'excel'
            },callback=self.download_dce_kline_data,meta={
                'filename':the_dir
            }))
        return requests

    def request_history_kdata(self):
        return [Request(url="http://www.dce.com.cn/dalianshangpin/xqsj/lssj/index.html",callback=self.download_dce_history_data)]


    def download_dce_history_data(self,response):
        the_dir = get_exchange_cache_dir(security_type='future', exchange='dce')
        for filepath in response.css('input').xpath('@rel').extract():
            yield Request(url="http://www.dce.com.cn/"+filepath,
                      meta={'filename':os.path.join(the_dir,filepath.split("/")[-1])},
                      callback=self.download_dce_history_data_file)


    def download_dce_kline_data(self,response):
        content_type_header = response.headers.get('content-type', None)
        if content_type_header is None:
            content_type_header = response.headers.get('Content-Type',None)
        the_path = response.meta['filename']

        if content_type_header.decode("utf-8") == 'application/zip' or content_type_header.decode("utf-8") == 'text/csv' or content_type_header.decode("utf-8") == 'application/octet-stream;charset=utf-8':
            with open(the_path, "wb") as f:
                f.write(response.body)
                f.flush()

        else:
            self.logger.error(
                "get dce year kline data failed:the_path={} url={} content type={} ".format(
                                                                                                 the_path,
                                                                                                 response.url,
                                                                                                 content_type_header))

    def download_dce_history_data_file(self,response):
        content_type_header = response.headers.get('content-type', None)
        the_path = response.meta['filename']

        if content_type_header.decode("utf-8") == 'application/zip' or content_type_header.decode("utf-8") == 'text/csv':
            with open(the_path, "wb") as f:
                f.write(response.body)
                f.flush()

        else:
            self.logger.error(
                "get shfe year  data failed:the_path={} url={} content type={} ".format(
                                                                                                 the_path,
                                                                                                 response.url,
                                                                                                 content_type_header))
