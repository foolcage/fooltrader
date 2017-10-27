import datetime
import json
import os

import scrapy
from kafka import KafkaProducer
from scrapy import Request
from scrapy import Selector
from scrapy import signals

from fooltrader import settings
from fooltrader.consts import DEFAULT_KDATA_HEADER
from fooltrader.items import KDataFuquanItem, KDataItem
from fooltrader.settings import KAFKA_HOST, AUTO_KAFKA, STOCK_START_CODE, STOCK_END_CODE
from fooltrader.utils.utils import get_security_item, get_quarters, get_year_quarter, \
    get_sh_stock_list_path, get_sz_stock_list_path, get_kdata_path, get_trading_dates_path, get_trading_dates, \
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
            for fuquan in (False, True):
                data_path = get_kdata_path(item, year, quarter, fuquan)
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

        kdata_json = []
        trading_dates = []

        try:
            for tr in trs:
                tds = Selector(text=tr).xpath('//td//text()').extract()
                tds = [x.strip() for x in tds if x.strip()]
                if fuquan:
                    k_item = KDataFuquanItem(securityId=item['id'], code=item['code'], timestamp=tds[0], open=tds[1],
                                             high=tds[2], close=tds[3], low=tds[4], volume=tds[5], turnover=tds[6],
                                             fuquan=tds[7], type='stock', level='DAY')
                else:
                    k_item = KDataItem(securityId=item['id'], code=item['code'], timestamp=tds[0], open=tds[1],
                                       high=tds[2], close=tds[3], low=tds[4], volume=tds[5], turnover=tds[6],
                                       type='stock', level='DAY')
                kdata_json.append(dict(k_item))
                trading_dates.append(k_item['timestamp'])
                if AUTO_KAFKA:
                    self.producer.send('CHINA_STOCK_KDATA_DAY',
                                       bytes(json.dumps(dict(k_item), ensure_ascii=False), encoding='utf8'))

        except Exception as e:
            self.logger.error('error when getting k data url={} error={}'.format(response.url, e))

        if len(kdata_json) > 0:
            try:
                with open(path, "w") as f:
                    json.dump(kdata_json, f)
            except Exception as e:
                self.logger.error('error when saving k data url={} path={} error={}'.format(response.url, path, e))
        if len(trading_dates) > 0:
            path = get_trading_dates_path(item)
            current_dates = get_trading_dates(item)
            trading_dates = list(set(current_dates + trading_dates))
            trading_dates.sort()
            try:
                with open(get_trading_dates_path(item), "w") as f:
                    json.dump(trading_dates, f)
            except Exception as e:
                self.logger.error(
                    'error when saving trading dates url={} path={} error={}'.format(response.url, path, e))

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(StockKDataSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider, reason):
        spider.logger.info('Spider closed: %s,%s\n', spider.name, reason)

    def get_k_data_url(self, code, year, quarter, fuquan):
        if fuquan:
            return 'http://vip.stock.finance.sina.com.cn/corp/go.php/vMS_FuQuanMarketHistory/stockid/{}.phtml?year={}&jidu={}'.format(
                code, year, quarter)
        else:
            return 'http://vip.stock.finance.sina.com.cn/corp/go.php/vMS_MarketHistory/stockid/{}.phtml?year={}&jidu={}'.format(
                code, year, quarter)
