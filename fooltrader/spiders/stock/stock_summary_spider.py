import io
import threading

import demjson
import pandas as pd
import scrapy
from scrapy import Request
from scrapy import signals

from fooltrader.api.quote import get_kdata
from fooltrader.consts import DEFAULT_SH_SUMMARY_HEADER
from fooltrader.contract.data_contract import KDATA_COLUMN_INDEX
from fooltrader.contract.files_contract import get_kdata_path


class StockSummarySpider(scrapy.Spider):
    name = "stock_summary"

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.security_item = None
        self.sh_df = None
        self.sz_df = None
        self.file_lock = threading.RLock()

    def start_requests(self):
        self.security_item = self.settings.get("security_item")
        the_dates = self.settings.get("the_dates")
        # 上海市场概况放在 上证指数
        if self.security_item['id'] == 'index_sh_000001':
            self.sh_df = get_kdata(security_item=self.security_item)

            for the_date in the_dates:
                yield Request(
                    url='http://query.sse.com.cn/marketdata/tradedata/queryTradingByProdTypeData.do?jsonCallBack=jsonpCallback30731&searchDate={}&prodType=gp&_=1515717065511'.format(
                        the_date),
                    headers=DEFAULT_SH_SUMMARY_HEADER,
                    meta={'searchDate': the_date},
                    callback=self.download_sh_summary)
        # 深圳市场概况放在 深证综指
        elif self.security_item['id'] == 'index_sz_399106':
            self.sz_df = get_kdata(security_item=self.security_item)

            for the_date in the_dates:
                if pd.Timestamp(the_date).date().year >= 2005:
                    yield Request(
                        url='http://www.szse.cn/szseWeb/ShowReport.szse?SHOWTYPE=excel&CATALOGID=1803&txtQueryDate={}&ENCODE=1&TABKEY=tab1'.format(
                            the_date),
                        meta={'searchDate': the_date},
                        callback=self.download_sz_summary)

    def download_sz_summary(self, response):
        searchDate = response.meta['searchDate']
        df = pd.read_excel(io.BytesIO(response.body))
        print(df)

    def download_sh_summary(self, response):
        searchDate = response.meta['searchDate']

        results = demjson.decode(response.text[response.text.index("(") + 1:response.text.index(")")])['result']
        result = [result for result in results if result['productType'] == '1']
        if result and len(result) == 1:
            result_json = result[0]
            self.file_lock.acquire()
            # 有些较老的数据不存在,默认设为0.0
            try:
                self.sh_df.at[searchDate, 'pe'] = float(result_json['profitRate']) * 1.0
            except Exception as e:
                self.sh_df.at[searchDate, 'pe'] = 0.0
                self.logger.warn(e)

            try:
                self.sh_df.at[searchDate, 'tCap'] = float(result_json['marketValue1']) * 100000000
            except Exception as e:
                self.sh_df.at[searchDate, 'tCap'] = 0.0
                self.logger.warn(e)

            try:
                self.sh_df.at[searchDate, 'mCap'] = float(result_json['negotiableValue1']) * 100000000
            except Exception as e:
                self.sh_df.at[searchDate, 'mCap'] = 0.0
                self.logger.warn(e)

            try:
                self.sh_df.at[searchDate, 'turnoverRate'] = float(result_json['exchangeRate']) * 1.0
            except Exception as e:
                self.sh_df.at[searchDate, 'turnoverRate'] = 0.0
                self.logger.warn(e)

            self.file_lock.release()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(StockSummarySpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider, reason):
        self.sh_df = self.sh_df.loc[:, KDATA_COLUMN_INDEX]
        print(self.sh_df)
        self.sh_df.to_csv(get_kdata_path(item=self.security_item), index=False)
        spider.logger.info('Spider closed: %s,%s\n', spider.name, reason)
