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
