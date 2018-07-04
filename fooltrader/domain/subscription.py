# -*- coding: utf-8 -*-
from elasticsearch_dsl import Keyword, Nested, MetaField, Boolean, Date, datetime

from fooltrader.domain import BaseDocType

{
    "id": 123,
    "userId": 111,
    "securityType": "cryptocurrency",
    "exchange": "binance",
    "code": "BTC-USDT",
    "condition": {
        "upPct": 1,
        "downPct": 2,
        "up": 7000,
        "down": 6000,
        "cross": 0.02
    },
    "repeat": False
}


class Subscription(BaseDocType):
    id = Keyword()
    userId = Keyword()
    securityType = Keyword()
    exchange = Keyword()
    code = Keyword()
    condition = Nested()
    repeat = Boolean()

    class Meta:
        doc_type = 'doc'
        all = MetaField(enabled=False)


class CrossSubscription((BaseDocType)):
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
