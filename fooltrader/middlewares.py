# -*- coding: utf-8 -*-

import logging

from scrapy.exceptions import CloseSpider
from scrapy.spidermiddlewares.httperror import HttpErrorMiddleware, HttpError

from fooltrader import settings

logger = logging.getLogger(__name__)


# spider middleware
class FoolErrorMiddleware(HttpErrorMiddleware):
    def process_spider_exception(self, response, exception, spider):
        if isinstance(exception, HttpError):
            if response.status == 456:
                # response.meta['fool_blocked'] = True
                # return None
                raise CloseSpider('catch forbidden,close for a while')


# downloader middleware
class ForbiddenHandleMiddleware(object):
    forbidden_codes = (456, 403)

    def process_response(self, request, response, spider):
        proxy_count = len(settings.g_http_proxy_items)
        count = 0

        if request.meta.get('dont_proxy', False):
            return response
        if response.status in self.forbidden_codes:
            # 新浪财经
            if 'sina.com' in request.url:
                proxy_json = settings.g_http_proxy_items[count % proxy_count]
                count += 1
                if proxy_json['type'] == 'HTTPS':
                    proxy = 'https://{}:{}'.format(proxy_json['ip'], proxy_json['port'])
                elif proxy_json['type'] == 'HTTP':
                    proxy = 'http://{}:{}'.format(proxy_json['ip'], proxy_json['port'])
                request.meta['proxy'] = proxy
                logger.info("using")
                return request
        return response
