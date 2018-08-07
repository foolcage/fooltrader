# -*- coding: utf-8 -*-

import datetime
import logging
import os
import socket
import subprocess
import uuid
from contextlib import closing
from urllib.parse import urlsplit

import pandas as pd
import requests

from fooltrader.proxy import get_sorted_proxy_path, get_proxy, get_checked_proxy_path, get_checked_proxy_dir
from fooltrader.proxy.spiders.proxy_spider_hideme import ProxySpiderHideMe
from fooltrader.settings import DG_PATH, SUPPORT_SOCKS2HTTP, g_socks2http_proxy_items

logger = logging.getLogger(__name__)


# 由于scrapy不支持socks代理(https://github.com/scrapy/scrapy/issues/747)
# 需要做转发的可以使用http://www.delegate.org/documents/
def start_delegate(proxy):
    local_port = find_free_port()
    cmd = '{} ADMIN=nobdoy RESOLV="" -P:{} SERVER=http TIMEOUT=con:15 SOCKS={}:{}'.format(
        DG_PATH, local_port, proxy['ip'], proxy['port'])
    subprocess.Popen(cmd, shell=True)
    return {'ip': '127.0.0.1',
            'port': local_port,
            'location': 'fooltrader',
            'speed': '1',
            'type': 'http',
            'anonymity': 'high'
            }


def stop_delegate(localport):
    cmd = '{} -P:{} -Fkill'.format(DG_PATH, localport)
    subprocess.Popen(cmd, shell=True)


def release_socks2http_proxy():
    for _, item in g_socks2http_proxy_items:
        stop_delegate(item['port'])


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        return s.getsockname()[1]


def crawl_proxy():
    # 这是我自己搭的两个socks代理,需要使用的话,替换成自己的哈
    if SUPPORT_SOCKS2HTTP:
        my_1080 = {'ip': '127.0.0.1',
                   'port': 1080,
                   'location': 'fooltrader',
                   'speed': '1',
                   'type': 'socks',
                   'anonymity': 'high'
                   }
        my_1081 = {'ip': '127.0.0.1',
                   'port': 1081,
                   'location': 'fooltrader',
                   'speed': '1',
                   'type': 'socks',
                   'anonymity': 'high'
                   }
        g_socks2http_proxy_items['{}:{}'.format(my_1080['ip'], + my_1080['port'])] = start_delegate(my_1080)

        g_socks2http_proxy_items['{}:{}'.format(my_1081['ip'], + my_1081['port'])] = start_delegate(my_1081)
    # 抓取免费代理
    ProxySpiderHideMe().run()


def check_proxy(url):
    domain = "{0.netloc}".format(urlsplit(url))

    for protocol in ['http', 'https']:
        df = pd.DataFrame()
        df_proxies = get_proxy(protocol)
        for i, item in df_proxies.iterrows():
            try:
                start_time = datetime.datetime.now()
                r = requests.get(url, proxies={'http': item['url'],
                                               'https': item['url']}, timeout=30)
                if r.status_code == 200:
                    elapsed_time = datetime.datetime.now() - start_time
                    item['delay'] = elapsed_time.seconds
                    logger.info("{} got proxy:{} delay:{}s".format(url, item['url'], elapsed_time))
                    df = df.append(item)

                    df = df.drop_duplicates(subset=('url'), keep='last')
                    df = df.sort_values('delay')
                    # 这个检测较慢,满5个就先存一下
                    if len(df.index) == 5 or i == len(df_proxies.index) - 1:
                        part_name = uuid.uuid4()
                        if domain == 'www.baidu.com':
                            df.to_csv(get_checked_proxy_path(protocol=protocol, part_name=part_name),
                                      index=False)
                        else:
                            df.to_csv(get_sorted_proxy_path(domain=domain, protocol=protocol, part_name=part_name),
                                      index=False)
                        df = pd.DataFrame()

            except Exception as e:
                logger.exception("{} using proxy:{} error:{}".format(url, item['url'], e))


def merge_checked(remove_tmp=True):
    for protocol in ['http', 'https']:
        merge_path = get_checked_proxy_path(protocol)
        if os.path.exists(merge_path):
            df = pd.read_csv(merge_path)
        else:
            df = None

        the_dir = get_checked_proxy_dir('tmp')
        for f in os.listdir(the_dir):
            the_file = os.path.join(the_dir, f)
            if protocol in f and get_checked_proxy_path(protocol) != the_file:
                if df is None:
                    df = pd.read_csv(the_file)
                else:
                    df = df.append(pd.read_csv(the_file), ignore_index=True)

                if remove_tmp:
                    os.remove(the_file)

        if df is not None:
            df = df.drop_duplicates(subset=('url'), keep='last')
            df = df.sort_values('delay')
            df.to_csv(get_checked_proxy_path(protocol), index=False)


if __name__ == '__main__':
    # 抓取免费代理
    # crawl_proxy()
    # 检测有效代理
    # check_proxy("http://www.baidu.com")
    # 合并有效代理
    merge_checked()
