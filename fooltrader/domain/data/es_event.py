# -*- coding: utf-8 -*-

from elasticsearch_dsl import Keyword, Date, Float
from elasticsearch_dsl import MetaField

from fooltrader.domain import BaseDocType


class FinanceForecastEvent(BaseDocType):
    id = Keyword()
    timestamp = Date()

    reportPeriod = Date()
    securityId = Keyword()
    type = Keyword()
    description = Keyword()
    preEPS = Float()
    changeStart = Float()
    change = Float()

    class Meta:
        index = 'finance_forecast_event'
        doc_type = 'doc'
        all = MetaField(enabled=False)
        dynamic = MetaField('strict')


class FinanceReportEvent(BaseDocType):
    id = Keyword()
    timestamp = Date()

    reportPeriod = Date()
    securityId = Keyword()
    title = Keyword()
    url = Keyword()

    class Meta:
        index = 'finance_report_event'
        doc_type = 'doc'
        all = MetaField(enabled=False)
        dynamic = MetaField('strict')
