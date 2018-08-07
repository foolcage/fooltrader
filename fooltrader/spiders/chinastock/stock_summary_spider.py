# -*- coding: utf-8 -*-

import threading

import demjson
import pandas as pd
import scrapy
from scrapy import Request
from scrapy import Selector
from scrapy import signals

from fooltrader.api.technical import get_kdata
from fooltrader.consts import DEFAULT_SH_SUMMARY_HEADER
from fooltrader.contract.data_contract import KDATA_INDEX_COL
from fooltrader.contract.files_contract import get_kdata_path
from fooltrader.utils.utils import to_float


class StockSummarySpider(scrapy.Spider):
    name = "stock_summary"

    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 8,

        'SPIDER_MIDDLEWARES': {
            'fooltrader.middlewares.FoolErrorMiddleware': 1000,
        }
    }


    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.security_item = None
        self.current_df = None
        self.file_lock = threading.RLock()

    def start_requests(self):
        self.security_item = self.settings.get("security_item")
        self.current_df = get_kdata(security_item=self.security_item,start_date=self.security_item['listDate'])

        the_dates = self.settings.get("the_dates")
        # 上海市场概况放在 上证指数
        if self.security_item['id'] == 'index_sh_000001':
            for the_date in the_dates:
                yield Request(
                    url='http://query.sse.com.cn/marketdata/tradedata/queryTradingByProdTypeData.do?jsonCallBack=jsonpCallback30731&searchDate={}&prodType=gp&_=1515717065511'.format(
                        the_date),
                    headers=DEFAULT_SH_SUMMARY_HEADER,
                    meta={'search_date': the_date},
                    callback=self.download_sh_summary)
        # 深圳市场概况放在 深证综指
        elif self.security_item['id'] == 'index_sz_399106':
            for the_date in the_dates:
                if pd.Timestamp(the_date).date().year >= 2005:
                    yield Request(
                        url='http://www.szse.cn/szseWeb/ShowReport.szse?SHOWTYPE=excel&CATALOGID=1803&txtQueryDate={}&ENCODE=1&TABKEY=tab1'.format(
                            the_date),
                        meta={'search_date': the_date},
                        callback=self.download_sz_summary)
        # 中小板
        elif self.security_item['id'] == 'index_sz_399005':
            for the_date in the_dates:
                yield Request(
                    url='http://www.szse.cn/szseWeb/ShowReport.szse?SHOWTYPE=excel&CATALOGID=1803&txtQueryDate={}&ENCODE=1&TABKEY=tab3'.format(
                        the_date),
                    meta={'search_date': the_date},
                    callback=self.download_sz_summary)
        # 创业板
        elif self.security_item['id'] == 'index_sz_399006':
            for the_date in the_dates:
                yield Request(
                    url='http://www.szse.cn/szseWeb/ShowReport.szse?SHOWTYPE=excel&CATALOGID=1803&txtQueryDate={}&ENCODE=1&TABKEY=tab4'.format(
                        the_date),
                    meta={'search_date': the_date},
                    callback=self.download_sz_summary)

    def download_sz_summary(self, response):
        search_date = response.meta['search_date']
        trs = response.xpath('//table/tr').extract()

        turnOver = None
        if self.security_item['id'] == 'index_sz_399106':
            for tr in trs[1:]:
                str_list = Selector(text=tr).xpath('//td//text()').extract()
                if '股票总市值' in str_list[0]:
                    tCap = to_float(str_list[1], 0.0)
                elif '股票流通市值' in str_list[0]:
                    mCap = to_float(str_list[1], 0.0)
                elif '平均市盈率' in str_list[0]:
                    pe = to_float(str_list[1], 0.0)
                elif '平均换手率' in str_list[0]:
                    turnoverRate = to_float(str_list[1], 0.0)
        else:
            for tr in trs[1:]:
                str_list = Selector(text=tr).xpath('//td//text()').extract()
                if '上市公司市价总值' in str_list[0]:
                    tCap = to_float(str_list[1], 0.0)
                elif '上市公司流通市值' in str_list[0]:
                    mCap = to_float(str_list[1], 0.0)
                elif '平均市盈率' in str_list[0]:
                    pe = to_float(str_list[1], 0.0)
                elif '总成交金额' in str_list[0]:
                    turnOver = to_float(str_list[1], 0.0)
            if turnOver:
                turnoverRate = 100 * turnOver / tCap
        self.file_lock.acquire()
        # 有些较老的数据不存在,默认设为0.0
        self.current_df.at[search_date, 'pe'] = pe
        self.current_df.at[search_date, 'tCap'] = tCap
        self.current_df.at[search_date, 'mCap'] = mCap
        self.current_df.at[search_date, 'turnoverRate'] = turnoverRate
        self.file_lock.release()

    def download_sh_summary(self, response):
        search_date = response.meta['search_date']

        results = demjson.decode(response.text[response.text.index("(") + 1:response.text.index(")")])['result']
        result = [result for result in results if result['productType'] == '1']
        if result and len(result) == 1:
            result_json = result[0]
            self.file_lock.acquire()
            # 有些较老的数据不存在,默认设为0.0
            self.current_df.at[search_date, 'pe'] = to_float(result_json['profitRate'], 0.0)
            self.current_df.at[search_date, 'tCap'] = to_float(result_json['marketValue1'], 0.0) * 100000000
            self.current_df.at[search_date, 'mCap'] = to_float(result_json['negotiableValue1'], 0.0) * 100000000
            self.current_df.at[search_date, 'turnoverRate'] = to_float(result_json['exchangeRate'], 0.0)
            self.file_lock.release()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(StockSummarySpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider, reason):
        self.current_df = self.current_df.loc[:, KDATA_INDEX_COL]
        print(self.current_df)
        self.current_df.to_csv(get_kdata_path(item=self.security_item), index=False)
        spider.logger.info('Spider closed: %s,%s\n', spider.name, reason)
