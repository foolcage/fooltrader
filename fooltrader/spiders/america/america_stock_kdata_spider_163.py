# -*- coding: utf-8 -*-

import json
import os

import pandas as pd
import scrapy
from scrapy import Request
from scrapy import signals

from fooltrader.api.technical import get_security_list
from fooltrader.contract.data_contract import KDATA_COLUMN_163, KDATA_INDEX_COLUMN_163, \
    KDATA_INDEX_COL, KDATA_STOCK_COL
from fooltrader.contract.files_contract import get_kdata_path
from fooltrader.settings import US_STOCK_CODES
from fooltrader.utils.utils import to_time_str


class AmericaStockKdataSpider(scrapy.Spider):
    name = "americ_stock_kdata"

    custom_settings = {
        # 'DOWNLOAD_DELAY': 2,
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 8,

        'SPIDER_MIDDLEWARES': {
            'fooltrader.middlewares.FoolErrorMiddleware': 1000,
        }
    }

    # 指定日期的话，是用来抓增量数据的
    def yield_request(self, item, the_years=None):
        data_path = get_kdata_path(item, source='163')

        if not the_years:
            if not pd.isna(item['listDate']):
                # 163 could just provide the date after year 2002
                list_date_year_, list_date_month_, list_date_day_ = item['listDate'].split("-")
                the_years = range(max(int(list_date_year_), 2002), pd.Timestamp.today().year + 1)
            else:
                the_years = range(2005, pd.Timestamp.today().year + 1)

        for the_year in the_years:
            url = self.get_k_data_url(the_year, item['code'])
            yield Request(url=url, meta={'path': data_path, 'item': item},
                          callback=self.download_day_k_data)

    def start_requests(self):
        item = self.settings.get("security_item")
        start_date = self.settings.get("start_date")
        end_date = self.settings.get("end_date")

        today = pd.Timestamp.today()

        the_years = None

        if start_date and end_date:
            if (today - start_date).days <= 5:
                pass
            else:
                the_years = range(start_date.year, end_date.year + 1)

        if item is not None and the_years:
            for request in self.yield_request(item, the_years):
                yield request
        else:
            for _, item in get_security_list(exchanges=['nasdaq'], codes=US_STOCK_CODES).iterrows():
                for request in self.yield_request(item):
                    yield request

    def download_day_k_data(self, response):
        filename_ = response.meta['path']
        item = response.meta['item']

        try:
            # 已经保存的csv数据
            if os.path.exists(filename_):
                df_current = pd.read_csv(filename_, dtype=str)
                # 补全历史数据
                if 'name' not in df_current.columns:
                    df_current['name'] = item['name']
            else:
                pathname_ = os.path.dirname(filename_)
                if not os.path.isdir(pathname_):
                    os.makedirs(pathname_)
                    
                df_current = pd.DataFrame()

            tmp_str = response.text

            json_str = tmp_str[tmp_str.index('{'):tmp_str.index('}') + 1]
            tmp_json = json.loads(json_str)

            the_datas = tmp_json['data']

            # 开,高,收,低,量,幅
            the_jsons = []
            pre_json = None

            for the_data in the_datas:
                the_json = {'code': item['code'],
                            'securityId': item['id'],
                            'name': item['name'],
                            'timestamp': to_time_str(the_data[0]),
                            'open': the_data[1],
                            'high': the_data[2],
                            'close': the_data[3],
                            'low': the_data[4],
                            'volume': the_data[5],
                            'changePct': the_data[6]}
                # 有些数据位置不对
                real_high = max(the_data[1], the_data[2], the_data[3], the_data[4])
                if the_json['high'] != real_high:
                    if the_json['close'] == real_high:
                        the_json['close'], the_json['high'] = the_json['high'], the_json['close']
                    elif the_json['open'] == real_high:
                        the_json['open'], the_json['high'] = the_json['high'], the_json['open']
                    elif the_json['low'] == real_high:
                        the_json['low'], the_json['high'] = the_json['high'], the_json['low']

                real_low = min(the_data[1], the_data[2], the_data[3], the_data[4])
                if the_json['low'] != real_low:
                    if the_json['close'] == real_low:
                        the_json['close'], the_json['low'] = the_json['low'], the_json['close']
                    elif the_json['open'] == real_low:
                        the_json['open'], the_json['low'] = the_json['low'], the_json['open']
                    elif the_json['high'] == real_low:
                        the_json['high'], the_json['low'] = the_json['low'], the_json['high']

                # 成交额为估算
                avgPrice = (the_json['open'] + the_json['high'] + the_json['close'] + the_json['low']) / 4
                the_json['turnover'] = avgPrice * the_json['volume']
                if pre_json:
                    the_json['preClose'] = pre_json['close']
                    the_json['change'] = the_json['close'] - pre_json['close']

                # TODO:这些数据目前没有,后面补全
                the_json['turnoverRate'] = 0
                the_json['tCap'] = 0
                the_json['mCap'] = 0
                the_json['factor'] = 0

                pre_json = the_json
                the_jsons.append(the_json)

            # 合并到当前csv中
            df_current = df_current.append(the_jsons, ignore_index=True)

            if item['type'] == 'index':
                df_current = df_current.dropna(subset=KDATA_INDEX_COLUMN_163)
                # 保证col顺序
                df_current = df_current.loc[:, KDATA_INDEX_COL]
            else:
                df_current = df_current.dropna(subset=KDATA_COLUMN_163)
                # 保证col顺序
                df_current = df_current.loc[:, KDATA_STOCK_COL]

            df_current = df_current.drop_duplicates(subset='timestamp', keep='last')
            df_current = df_current.set_index(df_current['timestamp'], drop=False)
            df_current.index = pd.to_datetime(df_current.index)
            df_current = df_current.sort_index()
            df_current.to_csv(filename_, index=False)
        except Exception as e:
            self.logger.exception('error when getting k data url={} error={}'.format(response.url, e))

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(AmericaStockKdataSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider, reason):
        spider.logger.info('Spider closed: %s,%s\n', spider.name, reason)

    def get_k_data_url(self, the_year, code):
        return 'http://img1.money.126.net/data/us/kline/day/history/{}/{}.json'.format(the_year, code)
