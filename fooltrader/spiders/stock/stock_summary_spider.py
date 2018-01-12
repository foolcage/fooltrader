import threading

import demjson
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
        self.file_lock = threading.RLock()

    def start_requests(self):
        self.security_item = self.settings.get("security_item")
        the_dates = self.settings.get("the_dates")
        if self.security_item['id'] == 'index_sh_000001':
            self.sh_df = get_kdata(security_item=self.security_item)

            for the_date in the_dates:
                yield Request(
                    url='http://query.sse.com.cn/marketdata/tradedata/queryTradingByProdTypeData.do?jsonCallBack=jsonpCallback30731&searchDate={}&prodType=gp&_=1515717065511'.format(
                        the_date),
                    headers=DEFAULT_SH_SUMMARY_HEADER,
                    meta={'searchDate': the_date},
                    callback=self.download_stock_summary)

    def download_stock_summary(self, response):
        searchDate = response.meta['searchDate']

        results = demjson.decode(response.text[response.text.index("(") + 1:response.text.index(")")])['result']
        result = [result for result in results if result['productType'] == '1']
        if result and len(result) == 1:
            result_json = result[0]
            self.file_lock.acquire()
            self.sh_df.at[searchDate, 'pe'] = result_json['profitRate']
            self.sh_df.at[searchDate, 'tCap'] = result_json['marketValue1'] * 100000000
            self.sh_df.at[searchDate, 'mCap'] = result_json['negotiableValue1'] * 100000000
            self.sh_df.at[searchDate, 'turnoverRate'] = result_json['exchangeRate']
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
