import datetime
import os

import pandas as pd
import scrapy
from kafka import KafkaProducer
from scrapy import Request
from scrapy import Selector
from scrapy import signals

from fooltrader import settings
from fooltrader.consts import DEFAULT_KDATA_HEADER
from fooltrader.contract import data_contract
from fooltrader.contract.files_contract import get_kdata_path_csv
from fooltrader.settings import KAFKA_HOST, AUTO_KAFKA
from fooltrader.utils.utils import get_quarters, get_year_quarter, \
    get_security_items


class StockKDataSpider(scrapy.Spider):
    name = "stock_kdata"

    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 8,

        'SPIDER_MIDDLEWARES': {
            'fooltrader.middlewares.FoolErrorMiddleware': 1000,
        }
    }

    if AUTO_KAFKA:
        producer = KafkaProducer(bootstrap_servers=KAFKA_HOST)

    def yield_request(self, item, start_date, end_date=None):
        if not start_date:
            start_date = item['listDate']
        if not end_date:
            end_date = datetime.date.today().strftime(settings.TIME_FORMAT_DAY)

        current_year, current_quarter = get_year_quarter(datetime.date.today())

        # get day k data
        for year, quarter in get_quarters(
                datetime.datetime.strptime(start_date, settings.TIME_FORMAT_DAY),
                datetime.datetime.strptime(end_date, settings.TIME_FORMAT_DAY)):
            for fuquan in ('hfq', 'bfq'):
                data_path = get_kdata_path_csv(item, year, quarter, fuquan)
                data_exist = os.path.isfile(data_path)

                # 该爬虫每天一次,一个季度一个文件，增量的数据在当前季度，所以总是下载
                if (current_quarter == quarter and current_year == year) \
                        or not data_exist \
                        or settings.FORCE_DOWNLOAD_KDATA:
                    url = self.get_k_data_url(item['code'], year, quarter, fuquan)
                    yield Request(url=url, headers=DEFAULT_KDATA_HEADER,
                                  meta={'path': data_path, 'item': item, 'fuquan': fuquan},
                                  callback=self.download_day_k_data)

    def start_requests(self):
        item = self.settings.get("security_item")
        start_date = self.settings.get("start_date")
        end_date = self.settings.get("end_date")
        if item:
            for request in self.yield_request(item, start_date, end_date):
                yield request
        else:
            for item in get_security_items():
                for request in self.yield_request(item, item['listDate']):
                    yield request

    def download_day_k_data(self, response):
        path = response.meta['path']
        item = response.meta['item']
        fuquan = response.meta['fuquan']
        trs = response.xpath('//*[@id="FundHoldSharesTable"]/tr[position()>1 and position()<=last()]').extract()

        try:
            if fuquan == 'hfq':
                df = pd.DataFrame(
                    columns=data_contract.KDATA_COLUMN_FQ)

            else:
                df = pd.DataFrame(
                    columns=data_contract.KDATA_COLUMN)

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
            self.logger.error('error when getting k data url={} error={}'.format(response.url, e))

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(StockKDataSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider, reason):
        spider.logger.info('Spider closed: %s,%s\n', spider.name, reason)

    def get_k_data_url(self, code, year, quarter, fuquan):
        if fuquan == 'hfq':
            return 'http://vip.stock.finance.sina.com.cn/corp/go.php/vMS_FuQuanMarketHistory/stockid/{}.phtml?year={}&jidu={}'.format(
                code, year, quarter)
        else:
            return 'http://vip.stock.finance.sina.com.cn/corp/go.php/vMS_MarketHistory/stockid/{}.phtml?year={}&jidu={}'.format(
                code, year, quarter)
