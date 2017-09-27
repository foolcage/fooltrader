# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SecurityItem(scrapy.Item):
    id = scrapy.Field()
    type = scrapy.Field()
    exchange = scrapy.Field()
    code = scrapy.Field()
    name = scrapy.Field()
    listDate = scrapy.Field()


class TickItem(scrapy.Item):
    security_id = scrapy.Field()
    time = scrapy.Field()
    price = scrapy.Field()
    volume = scrapy.Field()
    turnover = scrapy.Field()


class KDataFuquanItem(scrapy.Item):
    securityId = scrapy.Field()
    type = scrapy.Field()
    code = scrapy.Field()
    open = scrapy.Field()
    close = scrapy.Field()
    high = scrapy.Field()
    low = scrapy.Field()
    high = scrapy.Field()
    volume = scrapy.Field()
    turnover = scrapy.Field()
    timestamp = scrapy.Field()
    level = scrapy.Field()
    fuquan = scrapy.Field()


class KDataItem(scrapy.Item):
    securityId = scrapy.Field()
    type = scrapy.Field()
    code = scrapy.Field()
    open = scrapy.Field()
    close = scrapy.Field()
    high = scrapy.Field()
    low = scrapy.Field()
    high = scrapy.Field()
    volume = scrapy.Field()
    turnover = scrapy.Field()
    timestamp = scrapy.Field()
    level = scrapy.Field()


class SectorItem(scrapy.Item):
    id = scrapy.Field()
    start_date = scrapy.Field()
    name = scrapy.Field()
    link = scrapy.Field()
    type = scrapy.Field()
    producer = scrapy.Field()
    news_title = scrapy.Field()
    news_link = scrapy.Field()
    count = scrapy.Field()
    leadings = scrapy.Field()


class StockSectorItem(scrapy.Item):
    stock_id = scrapy.Field()
    sector_id = scrapy.Field()


class ProxyItem(scrapy.Item):
    ip = scrapy.Field();
    port = scrapy.Field();
    location = scrapy.Field();
    speed = scrapy.Field();
    type = scrapy.Field();
    anonymity = scrapy.Field();
