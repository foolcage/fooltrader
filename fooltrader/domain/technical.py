from elasticsearch_dsl import DocType, Keyword, Date, Float
from elasticsearch_dsl import MetaField


# 不复权
class BaseKData(DocType):
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


class BfqDayKData(BaseKData):
    class Meta:
        all = MetaField(enabled=False)
        doc_type = 'doc'


class HfqDayKData(BaseKData):
    factor = Float()

    class Meta:
        all = MetaField(enabled=False)
        doc_type = 'doc'
