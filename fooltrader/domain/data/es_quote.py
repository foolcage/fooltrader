# -*- coding: utf-8 -*-

from elasticsearch_dsl import Keyword, Date, Float
from elasticsearch_dsl import MetaField

from fooltrader.domain import BaseDocType


# ***********************************************************
# meta related
# ***********************************************************
# 股票元信息
class StockMeta(BaseDocType):
    id = Keyword()
    timestamp = Date()

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
        all = MetaField(enabled=False)
        dynamic = MetaField('strict')


# 指数元信息
class IndexMeta(BaseDocType):
    id = Keyword()
    timestamp = Date()

    type = Keyword()
    exchange = Keyword()
    code = Keyword()
    name = Keyword()
    listDate = Date()

    class Meta:
        index = 'index_meta'
        doc_type = 'doc'
        all = MetaField(enabled=False)
        dynamic = MetaField('strict')


# 数字货币元信息
class CryptocurrencyMeta(BaseDocType):
    id = Keyword()
    type = Keyword()
    exchange = Keyword()
    code = Keyword()
    name = Keyword()
    listDate = Date()
    timestamp = Date()

    class Meta:
        index = 'cryptocurrency_meta'
        doc_type = 'doc'
        all = MetaField(enabled=False)
        dynamic = MetaField('strict')


# ***********************************************************
# technical related
# ***********************************************************
class StockTickItem(BaseDocType):
    id = Keyword()
    timestamp = Date()
    securityId = Keyword()
    code = Keyword()

    price = Float()
    change = Float()
    direction = Keyword()
    volume = Float()
    turnover = Float()


# 股票K线
class StockKData(BaseDocType):
    id = Keyword()
    timestamp = Date()
    securityId = Keyword()
    code = Keyword()

    name = Keyword()
    open = Float()
    hfqOpen = Float()
    qfqOpen = Float()
    close = Float()
    hfqClose = Float()
    qfqClose = Float()
    high = Float()
    hfqHigh = Float()
    qfqHigh = Float()
    low = Float()
    hfqLow = Float()
    qfqLow = Float()
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
        doc_type = 'doc'
        all = MetaField(enabled=False)
        dynamic = MetaField('strict')


# 数字货币K线
class CryptoCurrencyKData(BaseDocType):
    id = Keyword()
    timestamp = Date()
    securityId = Keyword()
    code = Keyword()

    name = Keyword()
    open = Float()
    close = Float()
    high = Float()
    low = Float()
    volume = Float()
    preClose = Float()
    change = Float()
    changePct = Float()

    class Meta:
        doc_type = 'doc'
        all = MetaField(enabled=False)
        dynamic = MetaField('strict')


# 股票指数K线
class IndexKData(BaseDocType):
    id = Keyword()
    timestamp = Date()
    securityId = Keyword()
    code = Keyword()

    name = Keyword()
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
