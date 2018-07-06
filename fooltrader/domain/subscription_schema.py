# -*- coding: utf-8 -*-
from marshmallow import Schema, fields


class PriceConditionSchema(Schema):
    securityType = fields.Str()
    exchange = fields.Str()
    code = fields.Str()
    upPct = fields.Float()
    downPct = fields.Float()
    upTo = fields.Float()
    downTo = fields.Float()


class PriceSubscriptionSchema(Schema):
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
            "upTo": 7000,
            "downTo": 6000
        },
        "actions": ["weixin","email","shortMsg"],
        "repeat": False
    }
    """
    id = fields.Str()
    userId = fields.Str()
    type = fields.Str(default='price')
    condition = fields.Nested(PriceConditionSchema)
    repeat = fields.Boolean(missing=False)
    actions = fields.List(fields.String)
