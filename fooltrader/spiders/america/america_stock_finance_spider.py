import scrapy
from scrapy import Request
from scrapy import signals

from fooltrader.api.quote import get_security_list
from fooltrader.contract.files_contract import get_finance_path


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
            with open(path, "wb") as f:
                f.write(response.body)
                f.flush()
        else:
            self.logger.error(
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
