# -*- coding: utf-8 -*-

import io
import os
from datetime import datetime

import pandas as pd
import scrapy
from scrapy import Request
from scrapy import signals

from fooltrader.api.quote import parse_shfe_data
from fooltrader.contract.data_contract import KDATA_COLUMN_STOCK, KDATA_COLUMN_163
from fooltrader.contract.files_contract import get_kdata_path, get_exchange_cache_dir
from fooltrader.utils import utils


class FutureShfeSpider(scrapy.Spider):
    name = "future_shfe_spider"

    custom_settings = {
        # 'DOWNLOAD_DELAY': 2,
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 8,

    }

    # 指定日期的话，是用来抓增量数据的
    def yield_request(self, item, start_date=None, end_date=None):
        data_path = get_kdata_path(item, source='exchange')

        if start_date:
            start = start_date.strftime('%Y%m%d')
        else:
            start = item['listDate'].replace('-', '')

        if end_date:
            end = end_date.strftime('%Y%m%d')
        else:
            end = datetime.today().strftime('%Y%m%d')

        if not os.path.exists(data_path) or start_date or end_date:
            url = self.get_k_data_url()
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

    def download_day_k_data(self, response):
        path = response.meta['path']
        item = response.meta['item']

        try:
            # 已经保存的csv数据
            if os.path.exists(path):
                df_current = pd.read_csv(path, dtype=str)
            else:
                df_current = pd.DataFrame()

            df = utils.read_csv(io.BytesIO(response.body), encoding='GB2312', na_values='None')
            df['code'] = item['code']
            df['securityId'] = item['id']
            df = df.loc[:,
                 ['日期', 'code', '最低价', '开盘价', '收盘价', '最高价', '成交量', '成交金额', 'securityId', '前收盘', '涨跌额', '涨跌幅', '换手率',
                  '总市值', '流通市值']]
            df['factor'] = None
            df.columns = KDATA_COLUMN_STOCK

            # 合并到当前csv中
            df_current = df_current.append(df, ignore_index=True)

            df_current = df_current.dropna(subset=KDATA_COLUMN_163)
            df_current = df_current.drop_duplicates(subset='timestamp', keep='last')
            df_current = df_current.set_index(df_current['timestamp'])
            df_current.index = pd.to_datetime(df_current.index)
            df_current = df_current.sort_index()
            df_current.to_csv(path, index=False)
        except Exception as e:
            self.logger.error('error when getting k data url={} error={}'.format(response.url, e))

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
