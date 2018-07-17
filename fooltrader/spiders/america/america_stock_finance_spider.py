# -*- coding: utf-8 -*-

import io

import pandas as pd
import scrapy
from scrapy import Request
from scrapy import signals

from fooltrader.api.technical import get_security_list
from fooltrader.contract.files_contract import get_finance_path
from fooltrader.utils.utils import index_df_with_time


class AmericaStockFinanceSpider(scrapy.Spider):
    name = "america_stock_finance"

    custom_settings = {
        # 'DOWNLOAD_DELAY': 2,
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 8,

        'SPIDER_MIDDLEWARES': {
            'fooltrader.middlewares.FoolErrorMiddleware': 1000,
        }
    }

    def start_requests(self):
        security_item = self.settings.get("security_item")

        if security_item is not None:
            item = security_item
            data_url = self.get_finance_url(item['code'])
            data_path = get_finance_path(item)

            yield Request(url=data_url,
                          meta={'path': data_path,
                                'item': item},
                          callback=self.download_finance_csv)
        else:
            for _, item in get_security_list(exchanges=['nasdaq']).iterrows():
                data_url = self.get_finance_url(item['code'])
                data_path = get_finance_path(item)

                yield Request(url=data_url,
                              meta={'path': data_path,
                                    'item': item},
                              callback=self.download_finance_csv)

    def download_finance_csv(self, response):

        content_type_header = response.headers.get('content-type', None)

        if content_type_header.decode("utf-8") == content_type_header.decode("utf-8") == 'text/csv':
            path = response.meta['path']
            security_item = response.meta['item']

            df = pd.read_csv(io.BytesIO(response.body), na_values='None')
            df.columns = [
                "reportDate",
                "shares",
                "sharesAdjusted",
                "factor",
                "totalAssets",
                "totalCurrentAssets",
                "totalLiabilities",
                "totalCurrentLiabilities",
                "bookValue",
                "minorityBookValue",
                "preferredEquity",
                "goodwill",
                "longTermBorrowing",
                "operatingRevenue",
                "netProfit",
                "netProfitAttributedToParentCompanyOwner",
                "EPS",
                "dilutedEPS",
                "DPS",
                "netCashFlowsFromOperatingActivities",
                "netCashFlowsFromInvesting",
                "netCashFlowsFromFinancingActivities",
                "cashChange",
                "cashAtTheEndOfPeriod",
                "capitalExpenditures",
                "price",
                "priceHigh",
                "priceLow",
                "ROE",
                "ROA",
                "BVPS",
                "PB",
                "PE",
                "cumulativeDividendsPerShare",
                "dividendPayoutRatio",
                "longTermDebtToEquityRatio",
                "equityToAssetsRatio",
                "netMargin",
                "assetTurnover",
                "freeCashFlowPerShare",
                "currentRatio"]

            df['code'] = security_item['code']
            df['securityId'] = security_item['id']
            df['id'] = df[['securityId', 'reportDate']].apply(lambda x: '_'.join(x.astype(str)), axis=1)

            df = index_df_with_time(df, index='reportDate')

            df.fillna(0, inplace=True)

            df.to_csv(path, index=False)
        else:
            self.logger.exception(
                "get finance csv error:url={} content type={} body={}".format(response.url, content_type_header,
                                                                              response.body))

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(AmericaStockFinanceSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider, reason):
        spider.logger.info('Spider closed: %s,%s\n', spider.name, reason)

    def get_finance_url(self, code):
        return 'http://www.stockpup.com/data/{}_quarterly_financial_data.csv'.format(code)
