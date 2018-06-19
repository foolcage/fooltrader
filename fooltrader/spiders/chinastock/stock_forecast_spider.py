# -*- coding: utf-8 -*-

import json

import scrapy
from scrapy import Request
from scrapy import Selector
from scrapy import signals

from fooltrader.api.quote import get_security_list
from fooltrader.consts import DEFAULT_KDATA_HEADER
from fooltrader.contract.files_contract import get_forecast_event_path


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

                json_item = {"id": '{}_{}'.format(security_item['id'], tds[3]),
                             "securityId": security_item['id'],
                             "reportDate": tds[3],
                             "reportPeriod": tds[4],
                             "type": tds[2],
                             "description": tds[5],
                             "preEPS": preEPS,
                             "changeStart": change_start,
                             "change": change,
                             }
                forecast_jsons.append(json_item)

            if forecast_jsons:
                try:
                    with open(get_forecast_event_path(security_item), "w") as f:
                        json.dump(forecast_jsons, f, ensure_ascii=False)
                except Exception as e:
                    self.logger.error(
                        'error when saving forecast url={} path={} error={}'.format(response.url,
                                                                                    get_forecast_event_path(
                                                                                        security_item), e))



        except Exception as e:
            self.logger.error('error when getting k data url={} error={}'.format(response.url, e))

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
