import os
import re

import pandas as pd
import scrapy
from scrapy import Request
from scrapy import Selector
from scrapy import signals

from fooltrader.api.quote import get_security_list
from fooltrader.consts import DEFAULT_KDATA_HEADER
from fooltrader.contract.files_contract import get_event_path
from fooltrader.utils.utils import index_df_with_time


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
            # 一季度报告,中期报告,三季度报告,年度报告
            for period_type in ['yjdbg', 'zqbg', 'sjdbg', 'ndbg']:
                url = self.get_finance_report_event_url(item['code'], period_type)
                yield Request(url=url, headers=DEFAULT_KDATA_HEADER,
                              meta={'item': item,
                                    'period_type': period_type},
                              callback=self.download_fi_report_event_data)

    @staticmethod
    def report_period_from_title(title, period_type):
        year = re.match('.*(\d{4}).*', title).group(1)
        if period_type == 'yjdbg':
            return "{}0331".format(year)
        elif period_type == 'zqbg':
            return "{}0630".format(year)
        elif period_type == 'sjdbg':
            return "{}0930".format(year)
        elif period_type == 'ndbg':
            return "{}1231".format(year)

    def download_fi_report_event_data(self, response):
        security_item = response.meta['item']
        period_type = response.meta['period_type']

        path = get_event_path(security_item, event='finance_report')
        if os.path.exists(path):
            df = pd.read_csv(path)
            df = index_df_with_time(df, time_col='reportEventDate')
        else:
            df = pd.DataFrame()

        try:
            report_dates = response.xpath('//*[@id="con02-7"]/table[2]/tr/td[2]//ul/text()').extract()
            report_dates = [date.strip() for date in report_dates if date.strip()]

            report_contents = response.xpath('//*[@id="con02-7"]/table[2]/tr/td[2]//ul//a').extract()

            for i, tr in enumerate(report_contents):
                href = Selector(text=tr).xpath('//@href').extract()[0]
                title = Selector(text=tr).xpath('//text()').extract()[0]
                report_period = self.report_period_from_title(title, period_type)

                # 如果最新的事件已经抓取,直接返回
                if i == 0:
                    if not df.empty:
                        latest = df.index[-1].date()
                        if latest - pd.Timestamp(report_dates[0]).date() == 0 \
                                and df.loc[latest, 'title'] == title \
                                and df.loc[latest, 'reportDate'] == report_period:
                            return

                df = df.append({
                    "id": "{}_{}".format(report_dates[i], report_period),
                    "securityId": security_item['id'],
                    "reportEventDate": report_dates[i],
                    "url": "http://vip.stock.finance.sina.com.cn" + href,
                    "title": title,
                    "reportDate": report_period}, ignore_index=True)
            if not df.empty:
                df = index_df_with_time(df, time_col='reportEventDate')
                df.to_csv(path, index=False)
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
