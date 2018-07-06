# -*- coding: utf-8 -*-
from elasticsearch_dsl import Keyword, Nested, MetaField, Boolean, Date, datetime, Float

from fooltrader.domain import BaseDocType


class PriceCondition(BaseDocType):
    securityType = Keyword()
    exchange = Keyword()
    code = Keyword()
    upPct = Float()
    downPct = Float()
    upTo = Float()
    downTo = Float()


class PriceSubscription(BaseDocType):
    """
    {
        "id": 123,
        "userId": 111,
        "type": "price",
        "condition": {
            "securityType": "cryptocurrency",
            "exchange": "binance",
            "code": "BTC-USDT",
            "upPct": 1,
            "downPct": 2,
            "up": 7000,
            "down": 6000
        },
        "actions": [weixin,email,shortMsg],
        "repeat": False
    }
    """
    id = Keyword()
    userId = Keyword()
    condition = Nested(PriceCondition)
    repeat = Boolean()
    actions = Keyword()

    class Meta:
        doc_type = 'doc'
        all = MetaField(enabled=False)


class CrossCondition(BaseDocType):
    exchanges = Keyword()
    cross = Float()


class CrossSubscription(BaseDocType):
    id = Keyword()
    userId = Keyword()
    exchanges = Keyword()
    condition = Nested()
    repeat = Boolean()

    class Meta:
        doc_type = 'doc'
        all = MetaField(enabled=False)


class SubscriptionTriggered(BaseDocType):
    id = Keyword()
    subId = Keyword()
    timestamp = Date()

    class Meta:
        doc_type = 'doc'
        all = MetaField(enabled=False)

    def save(self, using=None, index=None, validate=True, force=True, **kwargs):
        # assign now if no timestamp given
        if not self.timestamp:
            self.timestamp = datetime.now()

        return super().save(using, index, validate, force, **kwargs)
