# -*- coding: utf-8 -*-

from elasticsearch_dsl import DocType, Keyword, Float, Nested, Date, Long, Short, Boolean
from elasticsearch_dsl import MetaField


class Account(DocType):
    # 机器人名字
    botName = Keyword()
    # 可用现金
    cash = Float()
    # 具体仓位
    positions = Nested()
    # 市值
    value = Float()
    # 市值+cash
    allValue = Float()
    # 时间
    timestamp = Date()

    # 收盘计算
    closing = Boolean()

    class Meta:
        index = 'account'
        doc_type = 'doc'
        all = MetaField(enabled=False)
        dynamic = MetaField('strict')


class Position(DocType):
    # 证券id
    securityId = Keyword()

    # 做多数量
    longAmount = Long()
    # 可平多数量
    availableLong = Long()
    # 平均做多价格
    averageLongPrice = Long()

    # 做空数量
    shortAmount = Long()
    # 可平空数量
    availableShort = Long()
    # 平均做空价格
    averageShortPrice = Long()

    # 市值 或者 占用的保证金(方便起见，总是100%)
    value = Float()
    # 交易类型(0代表T+0,1代表T+1)
    tradingT = Short()

    def __init__(self, meta=None, security_id=None, trading_t=1, **kwargs):
        super().__init__(meta, **kwargs)
        self.securityId = security_id
        self.longAmount = 0
        self.availableLong = 0
        self.shortAmount = 0
        self.availableShort = 0

        self.profit = 0
        self.value = 0
        self.tradingT = trading_t


class Order(DocType):
    # 订单id
    id = Keyword()
    # 交易员id
    botName = Keyword()
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
        dynamic = MetaField('strict')
