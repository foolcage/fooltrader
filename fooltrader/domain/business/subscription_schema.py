# -*- coding: utf-8 -*-
from marshmallow import Schema, fields


class PriceSubscriptionSchema(Schema):
    """
        {
            "id": 123,
            "userId": 111,
            "type": "price",
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
    id = fields.Str()
    userId = fields.Str()
    type = fields.Str(default='price')

    securityType = fields.Str()
    exchange = fields.Str()
    code = fields.Str()
    upPct = fields.Float()
    downPct = fields.Float()
    up = fields.Float()
    down = fields.Float()

    repeat = fields.Boolean(missing=False)
    actions = fields.List(fields.String)
