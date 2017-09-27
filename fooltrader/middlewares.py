from scrapy.exceptions import CloseSpider
from scrapy.spidermiddlewares.httperror import HttpErrorMiddleware, HttpError


class FoolErrorMiddleware(HttpErrorMiddleware):
    def process_spider_exception(self, response, exception, spider):
        if isinstance(exception, HttpError):
            if response.status == 456:
                # response.meta['fool_blocked'] = True
                # return None
                raise CloseSpider('catch forbidden,close for a while')
