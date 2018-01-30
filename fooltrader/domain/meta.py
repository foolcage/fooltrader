from elasticsearch_dsl import DocType, Keyword, Date, Float
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
