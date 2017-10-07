import itertools
import json
import os

import scrapy
from kafka import KafkaProducer
from scrapy import Request
from scrapy import signals

from fooltrader import settings
from fooltrader.consts import DEFAULT_TICK_HEADER
from fooltrader.settings import KAFKA_HOST, AUTO_KAFKA, STOCK_START_CODE, STOCK_END_CODE
from fooltrader.utils.utils import get_security_item, get_sh_stock_list_path, get_trading_dates, get_tick_path, \
    is_available_tick, get_sz_stock_list_path, get_datetime, get_tick_item, mkdir_for_security, \
    get_kdata_item_with_date, \
    kdata_to_tick


class StockTickSpider(scrapy.Spider):
    name = "stock_tick"

    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 8,

        'SPIDER_MIDDLEWARES': {
            'fooltrader.middlewares.FoolErrorMiddleware': 1000,
        }
    }

    if AUTO_KAFKA:
        producer = KafkaProducer(bootstrap_servers=KAFKA_HOST)

    def start_requests(self):
        proxy_count = len(settings.g_http_proxy_items)
        count = 0

        for item in itertools.chain(get_security_item(get_sh_stock_list_path()),
                                    get_security_item(get_sz_stock_list_path())):
            if STOCK_START_CODE <= item['code'] <= STOCK_END_CODE:
                mkdir_for_security(item)
                for trading_date in get_trading_dates(item):
                    if get_datetime(trading_date) < get_datetime(settings.START_TICK_DATE) or get_datetime(
                            trading_date) < get_datetime(settings.AVAILABLE_TICK_DATE):
                        continue
                    path = get_tick_path(item, trading_date)

                    if os.path.isfile(path) and is_available_tick(path):
                        continue
                    # proxy_json = settings.g_http_proxy_items[count % proxy_count]
                    # count += 1
                    # proxy = 'http://{}:{}'.format(proxy_json['ip'], proxy_json['port'])
                    yield Request(url=self.get_tick_url(trading_date, item['exchange'] + item['code']),
                                  meta={'proxy': None,
                                        'path': path,
                                        'trading_date': trading_date,
                                        'item': item},
                                  headers=DEFAULT_TICK_HEADER,
                                  callback=self.download_tick)

    def download_tick(self, response):
        # self.logger.info('using proxy:{}'.format(response.meta['proxy']))
        content_type_header = response.headers.get('content-type', None)
        if content_type_header.decode("utf-8") == 'application/vnd.ms-excel' or "当天没有数据" in response.body.decode(
                'GB2312'):
            path = response.meta['path']
            trading_date = response.meta['trading_date']
            item = response.meta['item']
            if content_type_header.decode("utf-8") == 'application/vnd.ms-excel':
                content = response.body
            else:
                kdata_json = get_kdata_item_with_date(response.meta['item'], response.meta['trading_date'])
                content = kdata_to_tick(response.meta['item'], kdata_json).encode('GB2312')
            with open(path, "wb") as f:
                f.write(content)
                f.flush()
                if AUTO_KAFKA:
                    for tick_item in get_tick_item(path, trading_date, item):
                        self.producer.send('CHINA_STOCK_TICK',
                                           bytes(json.dumps(tick_item, ensure_ascii=False), encoding='utf8'))

        else:
            self.logger.error(
                "get tick error:url={} content type={} body={}".format(response.url, content_type_header,
                                                                       response.body))

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(StockTickSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider, reason):
        spider.logger.info('Spider closed: %s,%s\n', spider.name, reason)

    def get_tick_url(self, date, code):
        return 'http://market.finance.sina.com.cn/downxls.php?date={}&symbol={}'.format(date, code)
