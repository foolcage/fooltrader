# -*- coding: utf-8 -*-
from elasticsearch_dsl import DocType, Keyword, Nested, MetaField

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
    "interval": "1d"
}


class Subscription(DocType):
    id = Keyword()
    userId = Keyword()
    securityType = Keyword()
    exchange = Keyword()
    code = Keyword()
    condition = Nested()
    interval = Keyword()

    class Meta:
        doc_type = 'doc'
        all = MetaField(enabled=False)


class CrossSubscription(DocType):
    id = Keyword()
    userId = Keyword()
    exchanges = Keyword()
    condition = Nested()
    interval = Keyword()

    class Meta:
        doc_type = 'doc'
        all = MetaField(enabled=False)
