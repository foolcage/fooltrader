# -*- coding: utf-8 -*-

import logging

from fooltrader.proxy import save_http_proxy, save_socks_proxy, save_https_proxy

logger = logging.getLogger(__name__)


class BaseProxySpider(object):
    def run(self):
        pass

    def save_proxies(self, http_jsons, https_jsons, socks_jsons):
        if http_jsons:
            try:
                save_http_proxy(http_jsons)
            except Exception as e:
                logger.error("failed to save http proxy json:{}", e)

        if https_jsons:
            try:
                save_https_proxy(https_jsons)
            except Exception as e:
                logger.error("failed to save https proxy json:{}", e)

        if socks_jsons:
            try:
                save_socks_proxy(socks_jsons)
            except Exception as e:
                logger.error("failed to save socks proxy json:{}", e)
