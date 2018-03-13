# -*- coding: utf-8 -*-

import json
import logging
from ast import literal_eval

import elasticsearch.helpers
from elasticsearch_dsl import Index
from elasticsearch_dsl.connections import connections

from fooltrader import EXCHANGE_LIST_COL
from fooltrader.api.event import get_forecast_items
from fooltrader.api.finance import get_balance_sheet_items, get_income_statement_items, get_cash_flow_statement_items, \
    get_finance_summary_items
from fooltrader.api.quote import get_security_list, get_kdata
from fooltrader.contract.es_contract import get_es_kdata_index, get_es_forecast_event_index
from fooltrader.domain.event import ForecastEvent
from fooltrader.domain.finance import BalanceSheet, IncomeStatement, CashFlowStatement, FinanceSummary
from fooltrader.domain.quote import StockMeta, StockKData, IndexKData
from fooltrader.settings import ES_HOSTS, US_STOCK_CODES
from fooltrader.utils.utils import fill_doc_type, is_same_date

logger = logging.getLogger(__name__)

es = connections.create_connection(hosts=ES_HOSTS)


def es_index_mapping(index_name, doc_type, force=False):
    # 创建索引
    index = Index(index_name)
    index.doc_type(doc_type)

    if not index.exists():
        index.create()
    else:
        if force:
            index.upgrade()


def es_get_latest_record(index, time_field='timestamp', query=None):
    body = '''
{
    "query": {
        "match_all": {}
    },
    "size": 1,
    "sort": [
        {
            "timestamp": {
                "order": "desc"
            }
        }
    ]
}
'''
    if time_field != 'timestamp':
        body = body.replace('timestamp', time_field)

    body = literal_eval(body)
    if query:
        body['query'] = query

    try:
        logger.info("search index:{},body:{}".format(index, body))
        response = es.search(index=index, body=body)
        if response['hits']['hits']:
            return response['hits']['hits'][0]['_source']
    except Exception as e:
        logger.warning(e)
    return None


def stock_meta_to_es(force=False):
    es_index_mapping('stock_meta', StockMeta)
    start_date = None
    if not force:
        latest_record = es_get_latest_record('stock_meta', time_field='listDate')
        logger.info("latest_record:{}".format(latest_record))
        if latest_record:
            start_date = latest_record['listDate']

    actions = []
    for _, item in get_security_list(mode='es', start_date=start_date, exchanges=EXCHANGE_LIST_COL).iterrows():
        if start_date and is_same_date(start_date, item['listDate']):
            continue
        try:
            stock_meta = StockMeta(meta={'id': item['id']})
            fill_doc_type(stock_meta, json.loads(item.to_json()))
            actions.append(stock_meta.to_dict(include_meta=True))
        except Exception as e:
            logger.warn("wrong SecurityItem:{},error:{}", item, e)
    if actions:
        resp = elasticsearch.helpers.bulk(es, actions)
        logger.info(resp)


def stock_kdata_to_es(start='000001', end='666666', codes=US_STOCK_CODES, force=False):
    for _, security_item in get_security_list(start=start, end=end, exchanges=['sh', 'sz', 'nasdaq'],
                                              codes=codes).iterrows():
        # 创建索引
        index_name = get_es_kdata_index(security_item['type'], security_item['exchange'])
        es_index_mapping(index_name, StockKData)

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
        for _, kdata_item in get_kdata(security_item, start_date=start_date).iterrows():
            if start_date and is_same_date(start_date, kdata_item['timestamp']):
                continue

            try:
                id = '{}_{}'.format(kdata_item['securityId'], kdata_item['timestamp'])
                kdata = StockKData(meta={'id': id}, id=id)
                kdata.meta['index'] = index_name
                fill_doc_type(kdata, json.loads(kdata_item.to_json()))
                # kdata.save(index=index_name)
                actions.append(kdata.to_dict(include_meta=True))
            except Exception as e:
                logger.warn("wrong KdataDay:{},error:{}", kdata_item, e)
        if actions:
            resp = elasticsearch.helpers.bulk(es, actions)
            logger.info(resp)


def index_kdata_to_es(force=False):
    for _, security_item in get_security_list(security_type='index', exchanges=EXCHANGE_LIST_COL).iterrows():
        # 创建索引
        index_name = get_es_kdata_index(security_item['type'], security_item['exchange'])
        es_index_mapping(index_name, IndexKData)

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
        for _, kdata_item in get_kdata(security_item, start_date=start_date).iterrows():
            if start_date and is_same_date(start_date, kdata_item['timestamp']):
                continue

            try:
                id = '{}_{}'.format(kdata_item['securityId'], kdata_item['timestamp'])
                kdata = IndexKData(meta={'id': id}, id=id)
                kdata.meta['index'] = index_name
                fill_doc_type(kdata, json.loads(kdata_item.to_json()))
                # kdata.save(index=index_name)
                actions.append(kdata.to_dict(include_meta=True))
            except Exception as e:
                logger.warn("wrong KdataDay:{},error:{}", kdata_item, e)
        if actions:
            resp = elasticsearch.helpers.bulk(es, actions)
            logger.info(resp)


def balance_sheet_to_es(force=False):
    es_index_mapping('balance_sheet', BalanceSheet)
    for _, security_item in get_security_list().iterrows():
        try:
            start_date = None
            if not force:
                query = {
                    "term": {"securityId": ""}
                }
                query["term"]["securityId"] = security_item["id"]
                latest_record = es_get_latest_record(index='balance_sheet', time_field='reportDate', query=query)
                logger.info("latest_record:{}".format(latest_record))
                if latest_record:
                    start_date = latest_record['reportDate']
            actions = []
            for json_object in get_balance_sheet_items(security_item, start_date=start_date):
                if start_date and is_same_date(start_date, json_object['reportDate']):
                    continue

                balance_sheet = BalanceSheet(meta={'id': json_object['id']})
                fill_doc_type(balance_sheet, json_object)
                # balance_sheet.save()
                actions.append(balance_sheet.to_dict(include_meta=True))
            if actions:
                resp = elasticsearch.helpers.bulk(es, actions)
                logger.info(resp)
        except Exception as e:
            logger.warn("wrong BalanceSheet:{},error:{}", security_item, e)


def income_statement_to_es(force=False):
    es_index_mapping('income_statement', IncomeStatement)

    for _, security_item in get_security_list().iterrows():
        try:
            start_date = None
            if not force:
                query = {
                    "term": {"securityId": ""}
                }
                query["term"]["securityId"] = security_item["id"]
                latest_record = es_get_latest_record(index='income_statement', time_field='reportDate', query=query)
                logger.info("latest_record:{}".format(latest_record))
                if latest_record:
                    start_date = latest_record['reportDate']
            actions = []
            for json_object in get_income_statement_items(security_item, start_date=start_date):
                if start_date and is_same_date(start_date, json_object['reportDate']):
                    continue

                income_statement = IncomeStatement(meta={'id': json_object['id']})
                fill_doc_type(income_statement, json_object)
                # income_statement.save()
                actions.append(income_statement.to_dict(include_meta=True))
            if actions:
                resp = elasticsearch.helpers.bulk(es, actions)
                logger.info(resp)
        except Exception as e:
            logger.warn("wrong IncomeStatement:{},error:{}", security_item, e)


def cash_flow_statement_to_es(force=False):
    es_index_mapping('cash_flow_statement', CashFlowStatement)

    for _, security_item in get_security_list().iterrows():
        try:
            start_date = None
            if not force:
                query = {
                    "term": {"securityId": ""}
                }
                query["term"]["securityId"] = security_item["id"]
                latest_record = es_get_latest_record(index='cash_flow_statement', time_field='reportDate', query=query)
                logger.info("latest_record:{}".format(latest_record))
                if latest_record:
                    start_date = latest_record['reportDate']
            actions = []
            for json_object in get_cash_flow_statement_items(security_item, start_date=start_date):
                if start_date and is_same_date(start_date, json_object['reportDate']):
                    continue

                cash_flow_statement = CashFlowStatement(meta={'id': json_object['id']})
                fill_doc_type(cash_flow_statement, json_object)
                # cash_flow_statement.save()
                actions.append(cash_flow_statement.to_dict(include_meta=True))
            if actions:
                resp = elasticsearch.helpers.bulk(es, actions)
                logger.info(resp)
        except Exception as e:
            logger.warn("wrong CashFlowStatement:{},error:{}", security_item, e)


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
                resp = elasticsearch.helpers.bulk(es, actions)
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
    stock_kdata_to_es(start='999999', end='999999', force=True)
    # balance_sheet_to_es()
    # index_kdata_to_es(force=False)
    # cash_flow_statement_to_es()
    # forecast_event_to_es()
    # usa_stock_finance_to_es(force=True)
