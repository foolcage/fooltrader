from elasticsearch_dsl import DocType, Keyword, Date, Float
from elasticsearch_dsl.connections import connections

# Define a default Elasticsearch client
connections.create_connection(hosts=['localhost'])


class StockMeta(DocType):
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

    class Meta:
        index = 'stock_meta'
        doc_type = 'doc'


class StockTickItem(DocType):
    securityId = Keyword()
    code = Keyword()
    timestamp = Date()
    price = Float()
    change = Float()
    direction = Keyword()
    volume = Float()
    turnover = Float()
