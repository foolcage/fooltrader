# -*- coding: utf-8 -*-

import json
import logging

import elasticsearch.helpers

from fooltrader import es_client
from fooltrader.api.event import get_finance_forecast_event, get_finance_report_event
from fooltrader.api.fundamental import get_balance_sheet_items, get_income_statement_items, get_cash_flow_statement_items, \
    get_finance_summary_items
from fooltrader.api.technical import get_security_list, get_kdata
from fooltrader.contract.es_contract import get_es_kdata_index, get_es_finance_event_index
from fooltrader.domain.event import FinanceForecastEvent, FinanceReportEvent
from fooltrader.domain.finance import BalanceSheet, IncomeStatement, CashFlowStatement, FinanceSummary
from fooltrader.domain.quote import StockMeta, StockKData, IndexKData, CryptoCurrencyKData, IndexMeta
from fooltrader.domain.security_model import CryptocurrencyMeta
from fooltrader.settings import US_STOCK_CODES
from fooltrader.utils.es_utils import es_get_latest_record, es_index_mapping, es_get_latest_timestamp
from fooltrader.utils.utils import fill_doc_type, is_same_date

logger = logging.getLogger(__name__)


def security_meta_to_es(security_type='stock', force=False):
    if security_type == 'stock':
        doc_type = StockMeta
    elif security_type == 'cryptocurrency':
        doc_type = CryptocurrencyMeta
    elif security_type == 'index':
        doc_type = IndexMeta

    index_name = "{}_meta".format(security_type)

    es_index_mapping(index_name, doc_type)

    start_date = None
    if not force:
        start_date = es_get_latest_timestamp(index=index_name)
        logger.info("start_date:{}".format(start_date))

    actions = []
    for _, item in get_security_list(security_type=security_type, start_list_date=start_date).iterrows():
        try:
            security_meta = doc_type(meta={'id': item['id']})
            security_meta.meta['index'] = index_name
            fill_doc_type(security_meta, json.loads(item.to_json()))
            actions.append(security_meta.to_dict(include_meta=True))
        except Exception as e:
            logger.exception("wrong SecurityItem:{},error:{}".format(item, e))
    if actions:
        resp = elasticsearch.helpers.bulk(es_client, actions)
        logger.info(resp)


def kdata_to_es(start=None, end=None, security_type='stock', force=False):
    if security_type == 'stock':
        doc_type = StockKData
    elif security_type == 'index':
        doc_type = IndexKData
    elif security_type == 'cryptocurrency':
        doc_type = CryptoCurrencyKData

    for _, security_item in get_security_list(security_type=security_type, start_code=start, end_code=end).iterrows():
        # 创建索引
        index_name = get_es_kdata_index(security_item['type'], security_item['exchange'])
        es_index_mapping(index_name, doc_type)

        start_date = None

        if not force:
            query = {
                "term": {"securityId": ""}
            }
            query["term"]["securityId"] = security_item["id"]
            start_date = es_get_latest_timestamp(index_name, query=query)
            logger.info("start_date:{}".format(start_date))

        actions = []

        df_kdata = get_kdata(security_item, start_date=start_date)

        for _, kdata_item in df_kdata.iterrows():
            try:
                id = '{}_{}'.format(kdata_item['securityId'], kdata_item['timestamp'])
                kdata = doc_type(meta={'id': id}, id=id)
                kdata.meta['index'] = index_name
                kdata_json = json.loads(kdata_item.to_json())

                fill_doc_type(kdata, kdata_json)
                # kdata.save(index=index_name)
                actions.append(kdata.to_dict(include_meta=True))
            except Exception as e:
                logger.exception("wrong KdataDay:{},error:{}".format(kdata_item, e))
        if actions:
            resp = elasticsearch.helpers.bulk(es_client, actions)
            logger.info(resp)


def finance_sheet_to_es(sheet_type='balance_sheet', force=False):
    if sheet_type == 'balance_sheet':
        doc_type = BalanceSheet
    elif sheet_type == 'income_statement':
        doc_type = IncomeStatement
    elif sheet_type == 'cash_flow_statement':
        doc_type = CashFlowStatement

    es_index_mapping(sheet_type, doc_type)

    for _, security_item in get_security_list().iterrows():
        try:
            start_date = None
            if not force:
                query = {
                    "term": {"securityId": ""}
                }
                query["term"]["securityId"] = security_item["id"]
                start_date = es_get_latest_timestamp(index=sheet_type, time_field='reportPeriod', query=query)
                logger.info("start_date:{}".format(start_date))

            actions = []

            items = []
            if sheet_type == 'balance_sheet':
                items = get_balance_sheet_items(security_item, start_date=start_date)
            elif sheet_type == 'income_statement':
                items = get_income_statement_items(security_item, start_date=start_date)
            elif sheet_type == 'cash_flow_statement':
                items = get_cash_flow_statement_items(security_item, start_date=start_date)

            for json_object in items:
                if start_date and is_same_date(start_date, json_object['reportPeriod']):
                    continue

                the_doc = doc_type(meta={'id': json_object['id']})
                fill_doc_type(the_doc, json_object)
                # balance_sheet.save()
                actions.append(the_doc.to_dict(include_meta=True))
            if actions:
                resp = elasticsearch.helpers.bulk(es_client, actions)
                logger.info(resp)
        except Exception as e:
            logger.warning("{} wrong {},error:{}", security_item, sheet_type, e)


def usa_stock_finance_to_es(force=False):
    es_index_mapping('finance_summary', FinanceSummary)

    for _, security_item in get_security_list(exchanges=['nasdaq'], codes=US_STOCK_CODES).iterrows():
        try:
            start_date = None
            if not force:
                query = {
                    "term": {"securityId": ""}
                }
                query["term"]["securityId"] = security_item["id"]
                latest_record = es_get_latest_record(index='finance_summary', time_field='reportDate', query=query)
                logger.info("latest_record:{}".format(latest_record))
                if latest_record:
                    start_date = latest_record['reportDate']
            actions = []
            for _, json_object in get_finance_summary_items(security_item, start_date=start_date).iterrows():
                if start_date and is_same_date(start_date, json_object['reportDate']):
                    continue

                finance_summary = FinanceSummary(meta={'id': json_object['id']})
                fill_doc_type(finance_summary, json_object.to_dict())
                actions.append(finance_summary.to_dict(include_meta=True))
            if actions:
                resp = elasticsearch.helpers.bulk(es_client, actions)
                logger.info(resp)
        except Exception as e:
            logger.exception("wrong FinanceSummary:{},error:{}".format(security_item, e))


def finance_event_to_es(event_type='finance_forecast', force=False):
    index_name = get_es_finance_event_index(event_type)
    if event_type == 'finance_forecast':
        doc_type = FinanceForecastEvent
    elif event_type == 'finance_report':
        doc_type = FinanceReportEvent

    es_index_mapping(index_name, doc_type)

    for _, security_item in get_security_list().iterrows():
        try:
            start_date = None
            if not force:
                query = {
                    "term": {"securityId": ""}
                }
                query["term"]["securityId"] = security_item["id"]
                start_date = es_get_latest_timestamp(index=index_name, query=query)
                logger.info("start_date:{}".format(start_date))

            if event_type == 'finance_forecast':
                df_event = get_finance_forecast_event(security_item, start_date=start_date)
            elif event_type == 'finance_report':
                df_event = get_finance_report_event(security_item, start_date=start_date)

            actions = []

            for _, event_object in df_event.iterrows():
                the_event = doc_type(meta={'id': event_object['id']})
                fill_doc_type(the_event, event_object.to_dict())
                # forcast_event.save()
                actions.append(the_event.to_dict(include_meta=True))
            if actions:
                resp = elasticsearch.helpers.bulk(es_client, actions)
                logger.info(resp)
        except Exception as e:
            logger.exception("wrong {},error:{}".format(security_item, e))


if __name__ == '__main__':
    # security_meta_to_es()
    # stock_meta_to_es(force=True)

    security_meta_to_es(force=False)
    # kdata_to_es(start='300027', end='300028', force=True)
    # kdata_to_es(security_type='index')
    # balance_sheet_to_es()
    # index_kdata_to_es(force=False)
    # cash_flow_statement_to_es()
    # forecast_event_to_es()
    # usa_stock_finance_to_es(force=True)
