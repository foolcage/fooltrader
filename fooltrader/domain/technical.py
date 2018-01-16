from elasticsearch_dsl import DocType, Keyword, Date, Float
from elasticsearch_dsl import MetaField


class StockKData(DocType):
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


class IndexKData(DocType):
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
