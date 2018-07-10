# -*- coding: utf-8 -*-

import logging

from fooltrader.proxy import save_proxy

logger = logging.getLogger(__name__)


class BaseProxySpider(object):
    def run(self):
        pass

    def save_proxies(self, http_jsons, https_jsons, socks_jsons):
        if http_jsons:
            try:
                save_proxy(http_jsons, protocol='http')
            except Exception as e:
                logger.exception("failed to save http proxy json:{}", e)

        if https_jsons:
            try:
                save_proxy(https_jsons, protocol='https')
            except Exception as e:
                logger.exception("failed to save https proxy json:{}", e)

        if socks_jsons:
            try:
                save_proxy(socks_jsons, protocol='socks')
            except Exception as e:
                logger.exception("failed to save socks proxy json:{}", e)
