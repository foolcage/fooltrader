# -*- coding: utf-8 -*-
import logging
import os

import pandas as pd
import scrapy
from scrapy import Request
from scrapy import Selector
from scrapy import signals

from fooltrader.api.technical import get_security_list, kdata_exist, get_kdata, to_security_item
from fooltrader.consts import DEFAULT_KDATA_HEADER
from fooltrader.contract import data_contract, files_contract
from fooltrader.contract.files_contract import get_kdata_path, get_kdata_dir
from fooltrader.settings import STOCK_START_CODE, STOCK_END_CODE
from fooltrader.utils.pd_utils import pd_read_csv
from fooltrader.utils.utils import get_quarters, get_year_quarter

logger = logging.getLogger(__name__)


class StockKDataSinaSpider(scrapy.Spider):
    name = "stock_kdata_sina"

    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 8,

        'SPIDER_MIDDLEWARES': {
            'fooltrader.middlewares.FoolErrorMiddleware': 1000,
        }
    }

    # 如果需要代理请打开
    # @random_proxy
    def yield_request(self, item, trading_dates=[], fuquan=None):
        the_quarters = []
        if trading_dates:
            for the_date in trading_dates:
                the_quarters.append(get_year_quarter(the_date))
        else:
            the_quarters = get_quarters(item['listDate'])

        the_quarters = set(the_quarters)

        if fuquan:
            fuquans = [fuquan]
        else:
            fuquans = ['bfq', 'hfq']

        # get day k data
        for year, quarter in the_quarters:
            for fuquan in fuquans:
                data_path = get_kdata_path(item, source='sina', year=year, quarter=quarter, fuquan=fuquan)
                data_exist = os.path.exists(data_path) or kdata_exist(item, year, quarter, fuquan, source='sina')

                if not data_exist:
                    url = self.get_k_data_url(item['code'], year, quarter, fuquan)
                    yield Request(url=url, headers=DEFAULT_KDATA_HEADER,
                                  meta={'path': data_path, 'item': item, 'fuquan': fuquan},
                                  callback=self.download_day_k_data)

    def start_requests(self):
        # 两种模式:
        # 1)item,trading_dates不指定,用于全量下载数据
        # 2)指定，用于修复
        item = self.settings.get("security_item")
        trading_dates = self.settings.get("trading_dates")
        fuquan = self.settings.get("fuquan")
        if item is not None:
            for request in self.yield_request(item, trading_dates, fuquan):
                yield request
        else:
            for _, item in get_security_list(start_code=STOCK_START_CODE, end_code=STOCK_END_CODE).iterrows():
                for request in self.yield_request(item):
                    yield request

    def download_day_k_data(self, response):
        path = response.meta['path']
        item = response.meta['item']
        fuquan = response.meta['fuquan']
        trs = response.xpath('//*[@id="FundHoldSharesTable"]/tr[position()>1 and position()<=last()]').extract()

        try:
            if fuquan == 'hfq':
                df = pd.DataFrame(
                    columns=data_contract.KDATA_COLUMN_SINA_FQ)

            else:
                df = pd.DataFrame(
                    columns=data_contract.KDATA_COLUMN_SINA)

            for idx, tr in enumerate(trs):
                tds = Selector(text=tr).xpath('//td//text()').extract()
                tds = [x.strip() for x in tds if x.strip()]
                securityId = item['id']
                timestamp = tds[0]
                open = float(tds[1])
                high = float(tds[2])
                close = float(tds[3])
                low = float(tds[4])
                volume = tds[5]
                turnover = tds[6]
                if fuquan == 'hfq':
                    factor = tds[7]
                    df.loc[idx] = [timestamp, item['code'], low, open, close, high, volume, turnover, securityId,
                                   factor]
                else:
                    df.loc[idx] = [timestamp, item['code'], low, open, close, high, volume, turnover, securityId]
            df.to_csv(path, index=False)
        except Exception as e:
            self.logger.exception('error when getting k data url={} error={}'.format(response.url, e))

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(StockKDataSinaSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider, reason):
        spider.logger.info('Spider closed: %s,%s\n', spider.name, reason)
        StockKDataSinaSpider.merge_kdata_to_one(security_item=self.settings.get("security_item"),
                                                fuquan=self.settings.get("fuquan"))

    def get_k_data_url(self, code, year, quarter, fuquan):
        if fuquan == 'hfq':
            return 'http://vip.stock.finance.sina.com.cn/corp/go.php/vMS_FuQuanMarketHistory/stockid/{}.phtml?year={}&jidu={}'.format(
                code, year, quarter)
        else:
            return 'http://vip.stock.finance.sina.com.cn/corp/go.php/vMS_MarketHistory/stockid/{}.phtml?year={}&jidu={}'.format(
                code, year, quarter)

    @staticmethod
    def merge_to_current_kdata(security_item, df, fuquan='bfq'):
        df = df.set_index(df['timestamp'], drop=False)
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()

        df1 = get_kdata(security_item, source='sina', fuquan=fuquan)
        df1 = df1.append(df)

        df1 = df1.drop_duplicates(subset='timestamp', keep='last')
        df1 = df1.sort_index()

        the_path = files_contract.get_kdata_path(security_item, source='sina', fuquan=fuquan)
        if fuquan == 'hfq':
            df1 = df1.loc[:, data_contract.KDATA_COLUMN_SINA_FQ]
        else:
            df1 = df1.loc[:, data_contract.KDATA_COLUMN_SINA]
        df1.to_csv(the_path, index=False)

    @staticmethod
    def add_factor_to_163(security_item):
        path_163 = get_kdata_path(security_item, source='163', fuquan='bfq')
        df_163 = pd_read_csv(path_163)

        if 'factor' in df_163.columns:
            df = df_163[df_163['factor'].isna()]

            if df.empty:
                logger.info("{} 163 factor is ok", security_item['code'])
                return

        path_sina = get_kdata_path(security_item, source='sina', fuquan='hfq')
        df_sina = pd_read_csv(path_sina)

        df_sina = df_sina[~df_sina.index.duplicated(keep='first')]
        df_163['factor'] = df_sina['factor']
        df_163.to_csv(path_163, index=False)

    @staticmethod
    def merge_kdata_to_one(security_item=None, replace=False, fuquan='bfq'):
        if type(security_item) != 'NoneType':
            items = pd.DataFrame().append(security_item).iterrows()
        else:
            items = get_security_list().iterrows()

        if fuquan:
            fuquans = [fuquan]
        else:
            fuquans = ['bfq', 'hfq']

        for index, security_item in items:
            for fuquan in fuquans:
                dayk_path = get_kdata_path(security_item, source='sina', fuquan=fuquan)
                if fuquan == 'hfq':
                    df = pd.DataFrame(
                        columns=data_contract.KDATA_COLUMN_SINA_FQ)
                else:
                    df = pd.DataFrame(
                        columns=data_contract.KDATA_COLUMN_SINA)

                the_dir = get_kdata_dir(security_item, fuquan=fuquan)

                if os.path.exists(the_dir):
                    files = [os.path.join(the_dir, f) for f in os.listdir(the_dir) if
                             ('dayk.csv' not in f and os.path.isfile(os.path.join(the_dir, f)))]
                    for f in files:
                        df = df.append(pd.read_csv(f, dtype=str), ignore_index=True)
                if df.size > 0:
                    df = df.set_index(df['timestamp'])
                    df.index = pd.to_datetime(df.index)
                    df = df.sort_index()
                    logger.info("{} to {}".format(security_item['code'], dayk_path))
                    if replace:
                        df.to_csv(dayk_path, index=False)
                    else:
                        StockKDataSinaSpider.merge_to_current_kdata(security_item, df, fuquan=fuquan)

                for f in files:
                    logger.info("remove {}".format(f))
                    os.remove(f)

                if fuquan == 'hfq':
                    StockKDataSinaSpider.add_factor_to_163(security_item)


if __name__ == '__main__':
    item = to_security_item('600000', exchange=None)
    StockKDataSinaSpider.add_factor_to_163(item)
