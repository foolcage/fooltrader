# -*- coding: utf-8 -*-

import scrapy
from scrapy import Request
from scrapy import signals

from fooltrader.api.technical import get_security_list
from fooltrader.consts import DEFAULT_BALANCE_SHEET_HEADER
from fooltrader.contract.files_contract import get_balance_sheet_path, get_income_statement_path, \
    get_cash_flow_statement_path


class StockFinanceSpider(scrapy.Spider):
    name = "stock_finance"

    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 8,

        'SPIDER_MIDDLEWARES': {
            'fooltrader.middlewares.FoolErrorMiddleware': 1000,
        }
    }

    def start_requests(self):
        security_item = self.settings.get("security_item")
        finance_type = self.settings.get("report_type")
        if security_item is not None:
            for request in self.yield_request(security_item, finance_type):
                yield request
        else:
            for _, item in get_security_list().iterrows():
                for request in self.yield_request(item):
                    yield request

    def yield_request(self, item=None, finance_type=None):
        if finance_type == 'balance_sheet':
            url_and_path = [(self.get_balance_sheet_url(item['code']), get_balance_sheet_path(item))]
        elif finance_type == 'income_statement':
            url_and_path = [(self.get_income_statement_url(item['code']), get_income_statement_path(item))]
        elif finance_type == 'cash_flow':
            url_and_path = [(self.get_cash_flow_statement_url(item['code']), get_cash_flow_statement_path(item))]
        else:
            url_and_path = [
                (self.get_balance_sheet_url(item['code']), get_balance_sheet_path(item)),
                (self.get_income_statement_url(item['code']), get_income_statement_path(item)),
                (self.get_cash_flow_statement_url(item['code']), get_cash_flow_statement_path(item))]
        for (data_url, data_path) in url_and_path:
            yield Request(url=data_url,
                          meta={'path': data_path,
                                'item': item},
                          headers=DEFAULT_BALANCE_SHEET_HEADER,
                          callback=self.download_finance_sheet)

    def download_finance_sheet(self, response):
        content_type_header = response.headers.get('content-type', None)

        if content_type_header.decode("utf-8") == 'application/vnd.ms-excel':
            path = response.meta['path']
            item = response.meta['item']
            with open(path, "wb") as f:
                f.write(response.body)
                f.flush()
        else:
            self.logger.exception(
                "get finance sheet error:url={} content type={} body={}".format(response.url, content_type_header,
                                                                                response.body))

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(StockFinanceSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider, reason):
        spider.logger.info('Spider closed: %s,%s\n', spider.name, reason)

    def get_balance_sheet_url(self, code):
        return 'http://money.finance.sina.com.cn/corp/go.php/vDOWN_BalanceSheet/displaytype/4/stockid/{}/ctrl/all.phtml' \
            .format(code)

    def get_income_statement_url(self, code):
        return 'http://money.finance.sina.com.cn/corp/go.php/vDOWN_ProfitStatement/displaytype/4/stockid/{}/ctrl/all.phtml' \
            .format(code)

    def get_cash_flow_statement_url(self, code):
        return 'http://money.finance.sina.com.cn/corp/go.php/vDOWN_CashFlow/displaytype/4/stockid/{}/ctrl/all.phtml' \
            .format(code)
