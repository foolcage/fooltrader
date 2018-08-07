# -*- coding: utf-8 -*-

import pandas as pd
import scrapy
from scrapy import Request
from scrapy import Selector
from scrapy import signals

from fooltrader.api.technical import get_security_list
from fooltrader.consts import DEFAULT_KDATA_HEADER
# 业绩预告抓取
# 上市公司预计年度经营业绩将出现下列情形之一的，应当在会计年度结束后一个月内进行业绩预告，预计中期和第三季度业绩将出现下列情形之一的，可以进行业绩预告：
#
# （一）净利润为负值；
#
# （二）净利润与上年同期相比上升或者下降50％以上；
#
# （三）实现扭亏为盈。
from fooltrader.contract.data_contract import EVENT_STOCK_FINANCE_FORECAST_COL
from fooltrader.contract.files_contract import get_finance_forecast_event_path
from fooltrader.utils.utils import index_df_with_time


class StockForecastSpider(scrapy.Spider):
    name = "stock_forecast"

    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 8,

        'SPIDER_MIDDLEWARES': {
            'fooltrader.middlewares.FoolErrorMiddleware': 1000,
        }
    }

    def start_requests(self):
        for _, item in get_security_list().iterrows():
            url = self.get_forecast_url(item['code'])
            yield Request(url=url, headers=DEFAULT_KDATA_HEADER,
                          meta={'item': item, },
                          callback=self.download_forecast_data)

    def download_forecast_data(self, response):
        security_item = response.meta['item']
        trs = response.xpath('//*[@id="dataTable"]//tr').extract()

        forecast_jsons = []

        try:
            for tr in trs[1:]:
                tds = Selector(text=tr).xpath('//td//text()').extract()
                tds = [x.strip() for x in tds if x.strip()]

                # 业绩变动字符串转为float
                change_str = tds[7]
                change_start = None

                if '~' in change_str:
                    i = change_str.index('~')
                    change_start = change_str[0:i]
                    change = change_str[i + 1:]
                else:
                    change = change_str

                if change:
                    change = change.strip('%')
                    change = float(change) / 100
                if change_start:
                    change_start = change_start.strip('%')
                    change_start = float(change_start) / 100

                # preEPS可能为空
                preEPS = None
                try:
                    preEPS = float(tds[6])
                except Exception as e:
                    pass

                json_item = {"securityId": security_item['id'],
                             "timestamp": tds[3],
                             "reportPeriod": tds[4],
                             "type": tds[2],
                             "description": tds[5],
                             "preEPS": preEPS,
                             "changeStart": change_start,
                             "change": change,
                             }
                forecast_jsons.append(json_item)

            if forecast_jsons:
                df = pd.DataFrame(forecast_jsons)
                df = df.drop_duplicates()
                df = df[:, EVENT_STOCK_FINANCE_FORECAST_COL]
                df = index_df_with_time(df)
                df.to_csv(get_finance_forecast_event_path(security_item), index=False)


        except Exception as e:
            self.logger.exception('error when getting k data url={} error={}'.format(response.url, e))

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(StockForecastSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider, reason):
        spider.logger.info('Spider closed: %s,%s\n', spider.name, reason)

    def get_forecast_url(self, code):
        return 'http://vip.stock.finance.sina.com.cn/q/go.php/vFinanceAnalyze/kind/performance/index.phtml?symbol={}'.format(
            code)
