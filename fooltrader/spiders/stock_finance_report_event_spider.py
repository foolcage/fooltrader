import os

import pandas as pd
import scrapy
from scrapy import Request
from scrapy import Selector
from scrapy import signals

from fooltrader.api.quote import get_security_list
from fooltrader.consts import DEFAULT_KDATA_HEADER
from fooltrader.contract.files_contract import get_event_path


class StockFinanceReportEventSpider(scrapy.Spider):
    name = "stock_finance_report_event"

    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 8,

        'SPIDER_MIDDLEWARES': {
            'fooltrader.middlewares.FoolErrorMiddleware': 1000,
        }
    }

    def start_requests(self):
        for _, item in get_security_list().iterrows():
            for report_period in ['yjdbg', 'zqbg', 'sjdbg', 'ndbg']:
                url = self.get_finance_report_event_url(item['code'], report_period)
                yield Request(url=url, headers=DEFAULT_KDATA_HEADER,
                              meta={'item': item, },
                              callback=self.download_fi_report_event_data)

    def download_fi_report_event_data(self, response):
        security_item = response.meta['item']
        path = get_event_path(security_item, event='finance_report')
        if os.path.exists(path):
            df = pd.read_csv(path)
        else:
            df = pd.DataFrame()

        try:
            report_dates = response.xpath('//*[@id="con02-7"]/table[2]/tr/td[2]//ul/text()').extract()
            report_dates = [date.strip() for date in report_dates if date.strip()]

            report_contents = response.xpath('//*[@id="con02-7"]/table[2]/tr/td[2]//ul//a').extract()

            hrefs = []
            titles = []
            for tr in report_contents:
                href = Selector(text=tr).xpath('//@href').extract()
                content = Selector(text=tr).xpath('//text()').extract()
                hrefs.append(href[0])
                titles.append(content[0])
            for i, report_date in enumerate(report_dates):
                title = titles[i]
                df.append({"reportDate": report_date,
                           "url": "http://vip.stock.finance.sina.com.cn" + hrefs[i],
                           "title": title})




        except Exception as e:
            self.logger.error('error when getting k data url={} error={}'.format(response.url, e))

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(StockFinanceReportEventSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider, reason):
        spider.logger.info('Spider closed: %s,%s\n', spider.name, reason)

    def get_finance_report_event_url(self, code, report_period):
        return 'http://vip.stock.finance.sina.com.cn/corp/go.php/vCB_BulletinYi/stockid/{}/page_type/{}.phtml'.format(
            code, report_period)
