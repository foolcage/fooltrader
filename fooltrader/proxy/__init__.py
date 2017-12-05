import os

import pandas as pd

from fooltrader import settings


# 获取存档的代理列表

def get_proxy_dir():
    return os.path.join(settings.FILES_STORE, "proxy")


def get_http_proxy_path():
    return os.path.join(get_proxy_dir(), "http_proxy.json")


def get_https_proxy_path():
    return os.path.join(get_proxy_dir(), "https_proxy.json")


def get_socks_proxy_path():
    return os.path.join(get_proxy_dir(), "socks_proxy.json")


def get_http_proxy():
    if os.path.exists(get_http_proxy_path()):
        return pd.read_json(get_http_proxy_path())
    else:
        return pd.DataFrame()


def get_https_proxy():
    if os.path.exists(get_https_proxy_path()):
        return pd.read_json(get_https_proxy_path())
    else:
        return pd.DataFrame()


def get_socks_proxy():
    if os.path.exists(get_socks_proxy_path()):
        return pd.read_json(get_socks_proxy_path())
    else:
        return pd.DataFrame()


def save_http_proxy(proxies):
    global http_proxy_df
    http_proxy_df = http_proxy_df.append(proxies)
    http_proxy_df.drop_duplicates(subset=('ip', 'port'), keep='last')
    http_proxy_df.to_json(get_http_proxy_path(), orient='records')


def save_https_proxy(proxies):
    global https_proxy_df
    https_proxy_df = https_proxy_df.append(proxies)
    https_proxy_df.drop_duplicates(subset=('ip', 'port'), keep='last')
    https_proxy_df.to_json(get_https_proxy_path(), orient='records')


def save_socks_proxy(proxies):
    global socks_proxy_df
    socks_proxy_df = socks_proxy_df.append(proxies)
    socks_proxy_df.drop_duplicates(subset=('ip', 'port'), keep='last')
    socks_proxy_df.to_json(get_socks_proxy_path(), orient='records')


if not os.path.exists(get_proxy_dir()):
    os.makedirs(get_proxy_dir())

http_proxy_df = get_http_proxy()
https_proxy_df = get_https_proxy()
socks_proxy_df = get_socks_proxy()
