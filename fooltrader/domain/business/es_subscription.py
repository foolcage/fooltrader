# -*- coding: utf-8 -*-
from elasticsearch_dsl import Keyword, MetaField, Boolean, Date, Float
from marshmallow import Schema, fields

from fooltrader.domain import BaseDocType


class PriceSubscription(BaseDocType):
    """
        {
            "id": 123,
            "userId": 111,
            "securityType": "cryptocurrency",
            "exchange": "binance",
            "code": "BTC-USDT",
            "upPct": 1,
            "downPct": 2,
            "up": 7000,
            "down": 6000,
            "actions": ["weixin", "email", "shortMsg"],
            "repeat": False
        }
    """
    id = Keyword()
    timestamp = Date()
    userId = Keyword()
    securityId = Keyword()

    securityType = Keyword()
    exchange = Keyword()
    code = Keyword()
    upPct = Float()
    downPct = Float()
    upTo = Float()
    downTo = Float()

    repeat = Boolean()
    actions = Keyword()

    class Meta:
        doc_type = 'doc'
        all = MetaField(enabled=False)
        dynamic = MetaField('strict')


class PriceSubscriptionSchema(Schema):
    id = fields.Str()
    userId = fields.Str(required=True)

    securityType = fields.Str(required=True)
    exchange = fields.Str(required=True)
    code = fields.Str(required=True)
    upPct = fields.Float()
    downPct = fields.Float()
    upTo = fields.Float()
    downTo = fields.Float()

    repeat = fields.Boolean(missing=False)
    actions = fields.List(fields.String)


class CrossSubscription(BaseDocType):
    id = Keyword()
    timestamp = Date()
    userId = Keyword()

    exchanges = Keyword()
    cross = Float()

    repeat = Boolean()
    actions = Keyword()

    class Meta:
        doc_type = 'doc'
        all = MetaField(enabled=False)
        dynamic = MetaField('strict')


class SubscriptionTriggered(BaseDocType):
    id = Keyword()
    timestamp = Date()

    subId = Keyword()
    subType = Keyword()
    conditionType = Keyword()

    class Meta:
        doc_type = 'doc'
        all = MetaField(enabled=False)
        dynamic = MetaField('strict')
