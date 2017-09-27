from elasticsearch_dsl import DocType, Keyword, Float, Nested, Date, Long, Short
from elasticsearch_dsl import MetaField


class Account(DocType):
    id = Keyword()
    traderId = Keyword()
    cash = Float()
    positions = Nested()
    timestamp = Date()

    class Meta:
        doc_type = 'doc'
        all = MetaField(enabled=False)


class Position(DocType):
    securityId = Keyword()
    amount = Long()
    availableAmount = Long()
    profit = Float()
    value = Float()
    cost = Float()


class Order(DocType):
    id = Keyword()
    traderId = Keyword()
    securityId = Keyword()
    direction = Short()
    type = Keyword()
    price = Float()
    amount = Long()
    status = Keyword()
    timestamp = Date()

    class Meta:
        doc_type = 'doc'
        all = MetaField(enabled=False)
