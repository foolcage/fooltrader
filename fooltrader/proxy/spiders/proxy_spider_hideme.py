# -*- coding: utf-8 -*-

import datetime
import logging

from scrapy import Selector
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from fooltrader.proxy.base_proxy_spider import BaseProxySpider

logger = logging.getLogger(__name__)


# 该爬虫需要把selenium的chrome driver运行起来才能跑
# 对于那种各种js跳转的网站,用selenium是一个不错的方案
class ProxySpiderHideMe(BaseProxySpider):
    def __init__(self):
        BaseProxySpider.__init__(self)

    def run(self):
        PROXY = "socks5://127.0.0.1:1081"
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--proxy-server={}'.format(PROXY))
        chrome_options.add_argument('headless')

        chrome = webdriver.Chrome(chrome_options=chrome_options)

        for i in range(0, 1601, 64):
            the_url = 'https://hidemy.name/en/proxy-list/?start={}#list'.format(i)
            logger.info("crawling {}".format(the_url))

            chrome.get(the_url)
            element = WebDriverWait(chrome, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "proxy__t"))
            )

            trs = Selector(text=element.get_attribute('innerHTML')).xpath('//tr').extract()

            http_jsons = []
            https_jsons = []
            socks_jsons = []
            for tr in trs[1:]:
                tds = Selector(text=tr).xpath('//td//text()').extract()
                tds = [x.strip() for x in tds]

                location = tds[2]
                if tds[3]:
                    location = location + " " + tds[3]

                check_time_gap = int(tds[7].split()[0].strip())
                check_time = (datetime.datetime.now() + datetime.timedelta(seconds=-check_time_gap)).strftime(
                    '%Y-%m-%d %H:%M:%S')

                if 'HTTP' in tds[5]:
                    the_url = "{}://{}:{}".format('http', tds[0], tds[1])
                elif 'HTTPS' in tds[5]:
                    the_url = "{}://{}:{}".format('https', tds[0], tds[1])
                elif 'SOCKS5' in tds[5]:
                    the_url = "{}://{}:{}".format('socks5', tds[0], tds[1])
                elif 'SOCKS4' in tds[5]:
                    the_url = "{}://{}:{}".format('socks4', tds[0], tds[1])
                else:
                    logger.info("not support protocol:{}".format(tds[5]))
                    continue

                json_item = {"url": the_url,
                             'location': location,
                             'anonymity': tds[6]}

                logger.info("get item {}".format(json_item))

                if 'HTTP' in tds[5]:
                    http_jsons.append(json_item)
                elif 'HTTPS' in tds[5]:
                    https_jsons.append(json_item)
                elif 'SOCKS' in tds[5]:
                    socks_jsons.append(json_item)
            self.save_proxies(http_jsons, https_jsons, socks_jsons)
