# -*- coding: utf-8 -*-

from elasticsearch_dsl import DocType, Keyword, Date, Text, Float
from elasticsearch_dsl import MetaField

from fooltrader.domain import BaseDocType


class ForecastEvent(BaseDocType):
    id = Keyword()
    securityId = Keyword()
    reportDate = Date()
    reportPeriod = Date()
    type = Keyword()
    description = Text()
    preEPS = Float()
    changeStart = Float()
    change = Float()

    class Meta:
        doc_type = 'doc'
        all = MetaField(enabled=False)


class FinanceReportEvent(BaseDocType):
    id = Keyword()
    securityId = Keyword()
    reportEventDate = Date()
    reportDate = Date()
    title = Keyword()
    url = Keyword()
