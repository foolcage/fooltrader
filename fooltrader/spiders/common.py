# -*- coding: utf-8 -*-
import functools
import random

from fooltrader.proxy import get_checked_proxy


def random_proxy(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        for request in func(*args, **kwargs):
            proxy_df = get_checked_proxy()
            if proxy_df is not None:
                request._meta['proxy'] = proxy_df.at[random.choice(proxy_df.index), 'url']
            yield request

    return wrapper
