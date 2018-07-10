# -*- coding: utf-8 -*-

import scrapy
from scrapy import Request
from scrapy.selector.unified import Selector

from fooltrader.consts import TONGHUASHUN_GN_HEADER
from fooltrader.items import SectorItem


class StockGNSpider(scrapy.Spider):
    name = "stock_gn_spider"
    custom_settings = {
        "ITEM_PIPELINES": {'fooltrader.pipelines.GetFilesPipeline': 1}}

    def start_requests(self):
        yield Request(
            url=self.get_gn_url(1),
            headers=TONGHUASHUN_GN_HEADER,
            meta={'index': 1},
            callback=self.parse_item)

    def parse_item(self, response):
        index = response.meta['index']
        if index == 1:
            index_count = response.selector.xpath('//*[@id="m-page"]/span/text()').extract()
            index_count = [x.strip() for x in index_count if x.strip()]
            index, count = [int(x) for x in index_count[0].split('/')]
            for i in range(index + 1, count + 1):
                yield Request(url=self.get_gn_url(i), headers=TONGHUASHUN_GN_HEADER,
                              meta={'index': i},
                              callback=self.parse_item)

        trs = response.xpath('/html/body/table/tbody//tr').extract()

        try:
            for tr in trs:
                start_date = Selector(text=tr).xpath('//td[1]/text()').extract_first()
                name = Selector(text=tr).xpath('//td[2]/a/text()').extract_first()
                link = Selector(text=tr).xpath('//td[2]/a/@href').extract_first()
                news_title = Selector(text=tr).xpath('//td[3]/a/text()').extract_first()
                news_link = Selector(text=tr).xpath('//td[3]/a/@href').extract_first()
                leadings = [x.rsplit('/')[-2] for x in Selector(text=trs[0]).xpath('//td[4]/a/@href').extract()]
                count = Selector(text=tr).xpath('//td[5]/text()').extract()
                yield SectorItem(id='{}_{}_{}'.format('10jqka', 'gn', name), start_date=start_date, name=name,
                                 link=link, news_title=news_title, news_link=news_link, leadings=leadings, count=count,
                                 producer='10jqka', type='gn')
        except Exception as e:
            self.logger.exception('error parse 10jqka gainian sector url:{} {}'.format(response.url, e))

    def get_gn_url(self, index):
        return 'http://q.10jqka.com.cn/gn/index/field/addtime/order/desc/page/{}/ajax/1'.format(index)
