# -*- coding: utf-8 -*-

import json
import logging

import elasticsearch.helpers
from elasticsearch_dsl import Index, connections

from fooltrader import EXCHANGE_LIST_COL, es_client
from fooltrader.api.event import get_forecast_items
from fooltrader.api.finance import get_balance_sheet_items, get_income_statement_items, get_cash_flow_statement_items, \
    get_finance_summary_items
from fooltrader.api.quote import get_security_list, get_kdata
from fooltrader.contract.es_contract import get_es_kdata_index, get_es_forecast_event_index
from fooltrader.domain.event import ForecastEvent
from fooltrader.domain.finance import BalanceSheet, IncomeStatement, CashFlowStatement, FinanceSummary
from fooltrader.domain.quote import StockMeta, StockKData, IndexKData, CryptoCurrencyKData
from fooltrader.domain.security_model import CryptoCurrencyMeta
from fooltrader.settings import US_STOCK_CODES, ES_HOSTS
from fooltrader.utils.es_utils import es_get_latest_record
from fooltrader.utils.utils import fill_doc_type, is_same_date

logger = logging.getLogger(__name__)


def es_index_mapping(index_name, doc_type, force=False):
    # 创建索引
    index = Index(index_name)
    index.doc_type(doc_type)

    if not index.exists():
        index.create()
    else:
        if force:
            index.upgrade()


def stock_meta_to_es(force=False):
    es_index_mapping('stock_meta', StockMeta)
    start_date = None
    if not force:
        latest_record = es_get_latest_record('stock_meta', time_field='listDate')
        logger.info("latest_record:{}".format(latest_record))
        if latest_record:
            start_date = latest_record['listDate']

    actions = []
    for _, item in get_security_list(mode='es', start_list_date=start_date, exchanges=EXCHANGE_LIST_COL).iterrows():
        if start_date and is_same_date(start_date, item['listDate']):
            continue
        try:
            stock_meta = StockMeta(meta={'id': item['id']})
            fill_doc_type(stock_meta, json.loads(item.to_json()))
            actions.append(stock_meta.to_dict(include_meta=True))
        except Exception as e:
            logger.warn("wrong SecurityItem:{},error:{}", item, e)
    if actions:
        resp = elasticsearch.helpers.bulk(es_client, actions)
        logger.info(resp)


def security_meta_to_es(security_type='cryptocurrency', force=False):
    if security_type == 'cryptocurrency':
        doc_type = CryptoCurrencyMeta

    es_index_mapping('crypto_currency_meta', doc_type)
    start_date = None
    if not force:
        latest_record = es_get_latest_record('stock_meta', time_field='listDate')
        logger.info("latest_record:{}".format(latest_record))
        if latest_record:
            start_date = latest_record['listDate']

    actions = []
    for _, item in get_security_list(security_type=security_type).iterrows():
        if start_date and item['listDate'] and is_same_date(start_date, item['listDate']):
            continue
        try:
            security_meta = doc_type(meta={'id': item['id']})
            fill_doc_type(security_meta, json.loads(item.to_json()))
            actions.append(security_meta.to_dict(include_meta=True))
        except Exception as e:
            logger.warn("wrong SecurityItem:{},error:{}", item, e)
    if actions:
        resp = elasticsearch.helpers.bulk(es_client, actions)
        logger.info(resp)


def kdata_to_es(start=None, end=None, security_type='stock', exchanges=['sh', 'sz'], force=False):
    if security_type == 'stock':
        doc_type = StockKData
    elif security_type == 'index':
        doc_type = IndexKData
    elif security_type == 'cryptocurrency':
        doc_type = CryptoCurrencyKData

    for _, security_item in get_security_list(security_type=security_type, exchanges=exchanges, start=start,
                                              end=end).iterrows():
        # 创建索引
        index_name = get_es_kdata_index(security_item['type'], security_item['exchange'])
        es_index_mapping(index_name, doc_type)

        start_date = None

        if not force:
            query = {
                "term": {"securityId": ""}
            }
            query["term"]["securityId"] = security_item["id"]
            latest_record = es_get_latest_record(index_name, query=query)
            logger.info("latest_record:{}".format(latest_record))
            if latest_record:
                start_date = latest_record['timestamp']
        actions = []

        df_kdata = get_kdata(security_item, start_date=start_date)

        for _, kdata_item in df_kdata.iterrows():
            if start_date and is_same_date(start_date, kdata_item['timestamp']):
                continue

            try:
                id = '{}_{}'.format(kdata_item['securityId'], kdata_item['timestamp'])
                kdata = doc_type(meta={'id': id}, id=id)
                kdata.meta['index'] = index_name
                kdata_json = json.loads(kdata_item.to_json())

                fill_doc_type(kdata, kdata_json)
                # kdata.save(index=index_name)
                actions.append(kdata.to_dict(include_meta=True))
            except Exception as e:
                logger.warn("wrong KdataDay:{},error:{}", kdata_item, e)
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
                latest_record = es_get_latest_record(index=sheet_type, time_field='reportDate', query=query)
                logger.info("latest_record:{}".format(latest_record))
                if latest_record:
                    start_date = latest_record['reportDate']
            actions = []

            items = []
            if sheet_type == 'balance_sheet':
                items = get_balance_sheet_items(security_item, start_date=start_date)
            elif sheet_type == 'income_statement':
                items = get_income_statement_items(security_item, start_date=start_date)
            elif sheet_type == 'cash_flow_statement':
                items = get_cash_flow_statement_items(security_item, start_date=start_date)

            for json_object in items:
                if start_date and is_same_date(start_date, json_object['reportDate']):
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
            logger.warn("wrong FinanceSummary:{},error:{}", security_item, e)


def forecast_event_to_es():
    for _, security_item in get_security_list().iterrows():
        # 创建索引
        index_name = get_es_forecast_event_index(security_item['id'])
        es_index_mapping(index_name, ForecastEvent)

        for json_object in get_forecast_items(security_item):
            try:
                forcast_event = ForecastEvent(meta={'id': json_object['id']})
                fill_doc_type(forcast_event, json_object)
                forcast_event.save()
            except Exception as e:
                logger.warn("wrong ForecastEvent:{},error:{}", json_object, e)


if __name__ == '__main__':
    # security_meta_to_es()
    # stock_meta_to_es(force=True)
    connections.create_connection(hosts=ES_HOSTS)
    security_meta_to_es(force=True)
    # kdata_to_es(start='300027', end='300028', force=True)
    # kdata_to_es(security_type='index')
    # balance_sheet_to_es()
    # index_kdata_to_es(force=False)
    # cash_flow_statement_to_es()
    # forecast_event_to_es()
    # usa_stock_finance_to_es(force=True)
