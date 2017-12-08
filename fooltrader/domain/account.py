from elasticsearch_dsl import DocType, Keyword, Float, Nested, Date, Long, Short
from elasticsearch_dsl import MetaField


class Account(DocType):
    traderId = Keyword()
    cash = Float()
    positions = Nested()
    timestamp = Date()

    class Meta:
        doc_type = 'doc'
        all = MetaField(enabled=False)


class Position(DocType):
    # 证券id
    securityId = Keyword()
    # 持有数量
    amount = Long()
    # 可交易数量
    availableAmount = Long()
    # 盈亏
    profit = Float()
    # 市值
    value = Float()
    # 成本价
    cost = Float()


class Order(DocType):
    # 订单id
    id = Keyword()
    # 交易员id
    traderId = Keyword()
    # 证券id
    securityId = Keyword()
    # 买卖(多空)
    direction = Short()
    # 市价/限价
    type = Keyword()
    # 价格
    price = Float()
    # 数量
    amount = Long()
    # 状态
    status = Keyword()
    # 时间
    timestamp = Date()

    class Meta:
        doc_type = 'doc'
        all = MetaField(enabled=False)
