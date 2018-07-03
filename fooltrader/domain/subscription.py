# -*- coding: utf-8 -*-
from elasticsearch_dsl import Keyword, Nested, MetaField, Boolean

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
