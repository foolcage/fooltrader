# -*- coding: utf-8 -*-
from fooltrader import get_security_list
from fooltrader.datamanager import process_crawl
from fooltrader.settings import US_STOCK_CODES
from fooltrader.spiders.america.america_list_spider import AmericaListSpider
from fooltrader.spiders.america.america_stock_kdata_spider_163 import AmericaStockKdataSpider


def crawl_usa_stock_data():
    # crawl the stock list
    process_crawl(AmericaListSpider, {})
    # crawl the kdata
    for _, security_item in get_security_list(security_type='stock', exchanges=['nasdaq'],
                                              codes=US_STOCK_CODES).iterrows():
        process_crawl(AmericaStockKdataSpider, {"security_item": security_item})
        # crawl the finance data
        # process_crawl(AmericaStockFinanceSpider, {"security_item": security_item})
        # crawl index data
        # process_crawl(Sp500Spider, {})
