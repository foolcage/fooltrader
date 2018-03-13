# -*- coding: utf-8 -*-

from elasticsearch_dsl import Keyword, Date, Float
from elasticsearch_dsl import MetaField
from elasticsearch_dsl.connections import connections

from fooltrader.domain import BaseDocType

connections.create_connection(hosts=['localhost'])


class StockMeta(BaseDocType):
    id = Keyword()
    type = Keyword()
    exchange = Keyword()
    code = Keyword()
    name = Keyword()
    listDate = Date()
    indexCategory = Keyword()
    sinaIndustry = Keyword()
    sinaConcept = Keyword()
    sinaArea = Keyword()
    sector = Keyword()
    industry = Keyword()

    class Meta:
        index = 'stock_meta'
        doc_type = 'doc'


class IndexMeta(BaseDocType):
    id = Keyword()
    type = Keyword()
    exchange = Keyword()
    code = Keyword()
    name = Keyword()
    listDate = Date()

    class Meta:
        index = 'index_meta'
        doc_type = 'doc'


class StockTickItem(BaseDocType):
    securityId = Keyword()
    code = Keyword()
    timestamp = Date()
    price = Float()
    change = Float()
    direction = Keyword()
    volume = Float()
    turnover = Float()


class StockKData(BaseDocType):
    id = Keyword()
    securityId = Keyword()
    timestamp = Date()
    code = Keyword()
    open = Float()
    close = Float()
    high = Float()
    low = Float()
    volume = Float()
    turnover = Float()
    preClose = Float()
    change = Float()
    changePct = Float()
    turnoverRate = Float()
    tCap = Float()
    mCap = Float()
    factor = Float()

    class Meta:
        all = MetaField(enabled=False)
        doc_type = 'doc'


class IndexKData(BaseDocType):
    id = Keyword()
    securityId = Keyword()
    timestamp = Date()
    code = Keyword()
    open = Float()
    close = Float()
    high = Float()
    low = Float()
    volume = Float()
    turnover = Float()
    preClose = Float()
    change = Float()
    changePct = Float()
    turnoverRate = Float()
    tCap = Float()
    mCap = Float()
    pe = Float()

    class Meta:
        all = MetaField(enabled=False)
        doc_type = 'doc'
