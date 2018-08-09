# -*- coding: utf-8 -*-

import json
import threading

import demjson
import scrapy
from scrapy import Request
from scrapy import signals

from fooltrader.api.technical import get_security_list
from fooltrader.contract.files_contract import get_security_list_path
from fooltrader.utils.utils import get_exchange


class SinaCategorySpider(scrapy.Spider):
    name = "sina_category"

    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 8,

        'SPIDER_MIDDLEWARES': {
            'fooltrader.middlewares.FoolErrorMiddleware': 1000,
        }
    }

    def start_requests(self):
        self.category_type = self.settings.get("category_type")

        self.sh_df = get_security_list(exchanges=['sh'])
        self.sz_df = get_security_list(exchanges=['sz'])
        self.file_lock = threading.RLock()

        # 清除老数据
        self.sh_df[self.category_type] = None
        self.sz_df[self.category_type] = None

        if self.category_type == 'sinaIndustry':
            url = 'http://vip.stock.finance.sina.com.cn/q/view/newSinaHy.php'
        elif self.category_type == 'sinaConcept':
            url = 'http://money.finance.sina.com.cn/q/view/newFLJK.php?param=class'
        elif self.category_type == 'sinaArea':
            url = 'http://money.finance.sina.com.cn/q/view/newFLJK.php?param=area'
        else:
            return

        yield Request(
            url=url,
            callback=self.download_sina_category)

    def download_sina_category(self, response):
        tmp_str = response.body.decode('GBK')
        json_str = tmp_str[tmp_str.index('{'):tmp_str.index('}') + 1]
        tmp_json = json.loads(json_str)
        for ind_code in tmp_json:
            for page in range(1, 4):
                yield Request(
                    url='http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page={}&num=1024&sort=symbol&asc=1&node={}&symbol=&_s_r_a=page'.format(
                        page, ind_code),
                    meta={'ind_code': ind_code,
                          'ind_name': tmp_json[ind_code].split(',')[1]},
                    callback=self.download_sina_category_detail)

    def download_sina_category_detail(self, response):
        if response.text == 'null' or response.text is None:
            return
        category_jsons = demjson.decode(response.text)
        for category in category_jsons:
            self.file_lock.acquire()
            if get_exchange(category['code']) == 'sh':
                df = self.sh_df
            elif get_exchange(category['code']) == 'sz':
                df = self.sz_df

            if category['code'] in df.index:
                current_ind = df.at[category['code'], self.category_type]

                if type(current_ind) == list and (response.meta['ind_name'] not in current_ind):
                    current_ind.append(response.meta['ind_name'])

                elif type(current_ind) == str and response.meta['ind_name'] != current_ind:
                    current_ind = [current_ind, response.meta['ind_name']]
                else:
                    current_ind = response.meta['ind_name']

                df.at[category['code'], self.category_type] = current_ind
            self.file_lock.release()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(SinaCategorySpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider, reason):
        if self.sh_df[self.category_type].any():
            self.sh_df.to_csv(get_security_list_path('stock', 'sh'), index=False)
        if self.sz_df[self.category_type].any():
            self.sz_df.to_csv(get_security_list_path('stock', 'sz'), index=False)
        spider.logger.info('Spider closed: %s,%s\n', spider.name, reason)