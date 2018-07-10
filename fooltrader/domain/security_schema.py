# -*- coding: utf-8 -*-
from marshmallow import Schema, fields
from marshmallow.fields import Date


class CryptoCurrencyMetaSchema(Schema):
    id = fields.Str()
    type = fields.Str()
    exchange = fields.Str()
    code = fields.Str()
    name = fields.Str()
    listDate = Date()
