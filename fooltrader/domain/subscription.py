# -*- coding: utf-8 -*-
from elasticsearch_dsl import DocType, Keyword, Nested, MetaField

{
    "id": 123,
    "alertType": 0,
    "condition": {
        "symbol": "BTC/USDT",
        "upPct": 1,
        "downPct": 2,
        "up": 7000,
        "down": 6000,
        "cross": 0.02
    },
    "interval": "1d"
}


class SymbolSubscription(DocType):
    id = Keyword()
    openId = Keyword()
    exchange = Keyword()
    condition = Nested()
    interval = Keyword()

    class Meta:
        doc_type = 'doc'
        all = MetaField(enabled=False)


class CrossSubscription(DocType):
    id = Keyword()
    openId = Keyword()
    exchanges = Keyword()
    condition = Nested()
    interval = Keyword()

    class Meta:
        doc_type = 'doc'
        all = MetaField(enabled=False)
