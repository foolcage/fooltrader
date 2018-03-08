# -*- coding: utf-8 -*-
import scrapy


class XinlangSpider(scrapy.Spider):
    name = 'xinlang'
    allowed_domains = ['http://finance.sina.com.cn/']
    start_urls = ['http://finance.sina.com.cn//']

    def parse(self, response):
        pass
