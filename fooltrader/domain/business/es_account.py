# -*- coding: utf-8 -*-

from elasticsearch_dsl import Keyword, Float, Nested, Date, Short, Boolean, InnerDoc
from elasticsearch_dsl import MetaField

from fooltrader.domain import BaseDocument
from fooltrader.utils.time_utils import to_time_str, TIME_FORMAT_ISO8601


class Position(InnerDoc):
    # 证券id
    securityId = Keyword()

    # 做多数量
    longAmount = Float()
    # 可平多数量
    availableLong = Float()
    # 平均做多价格
    averageLongPrice = Float()

    # 做空数量
    shortAmount = Float()
    # 可平空数量
    availableShort = Float()
    # 平均做空价格
    averageShortPrice = Float()

    profit = Float()
    # 市值 或者 占用的保证金(方便起见，总是100%)
    value = Float()
    # 交易类型(0代表T+0,1代表T+1)
    tradingT = Short()

    def __init__(self, security_id=None, trading_t=0, **kwargs):
        super().__init__(**kwargs)
        self.securityId = security_id
        self.longAmount = 0
        self.availableLong = 0
        self.averageLongPrice = 0
        self.shortAmount = 0
        self.availableShort = 0
        self.averageShortPrice = 0

        self.profit = 0
        self.value = 0
        self.tradingT = trading_t


class SimAccount(BaseDocument):
    id = Keyword()
    # 机器人名字
    traderName = Keyword()
    # 所用的模型
    modelName = Keyword()
    # 可用现金
    cash = Float()
    # 具体仓位
    positions = Nested(Position)
    # 市值
    value = Float()
    # 市值+cash
    allValue = Float()
    # 时间
    timestamp = Date()

    # 收盘计算
    closing = Boolean()

    class Meta:
        index = 'sim_account'
        doc_type = 'doc'
        all = MetaField(enabled=False)
        dynamic = MetaField('strict')

    def save(self, using=None, index=None, validate=True, force=True, refresh='wait_for', **kwargs):
        return super().save(using, index, validate, force, refresh=refresh, **kwargs)

    def to_dict(self, include_meta=False, skip_empty=True):
        self.id = "{}_{}_{}".format(self.traderName, self.modelName,
                                    to_time_str(self.timestamp, time_fmt=TIME_FORMAT_ISO8601))

        return super().to_dict(include_meta, skip_empty)


class Order(BaseDocument):
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
    amount = Float()
    # 状态
    status = Keyword()
    # 时间
    timestamp = Date()

    class Meta:
        doc_type = 'doc'
        all = MetaField(enabled=False)
        dynamic = MetaField('strict')
