import json
import logging

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Index
from elasticsearch_dsl.connections import connections

from fooltrader.api.event import get_forecast_items
from fooltrader.api.finance import get_balance_sheet_items, get_income_statement_items, get_cash_flow_statement_items
from fooltrader.api.quote import get_security_list, get_kdata
from fooltrader.contract.es_contract import get_es_kdata_index, get_es_forecast_event_index
from fooltrader.domain.event import ForecastEvent
from fooltrader.domain.finance import BalanceSheet, IncomeStatement, CashFlowStatement
from fooltrader.domain.meta import StockMeta
from fooltrader.domain.technical import StockKData, IndexKData
from fooltrader.settings import ES_HOSTS
from fooltrader.utils.utils import fill_doc_type

logger = logging.getLogger(__name__)

connections.create_connection(hosts=ES_HOSTS)
es = Elasticsearch()


def index_mapping(index_name, doc_type):
    # 创建索引
    index = Index(index_name)
    index.doc_type(doc_type)

    if not index.exists():
        index.create()
    else:
        index.upgrade()


def security_meta_to_es():
    index_mapping('stock_meta', StockMeta)
    for _, item in get_security_list(mode='es').iterrows():
        try:
            stock_meta = StockMeta(meta={'id': item['id']})
            fill_doc_type(stock_meta, json.loads(item.to_json()))
            stock_meta.save()
        except Exception as e:
            logger.warn("wrong SecurityItem:{},error:{}", item, e)


def stock_kdata_to_es():
    for _, security_item in get_security_list().iterrows():
        # 创建索引
        index_name = get_es_kdata_index(security_item['id'])
        index_mapping(index_name, StockKData)

        for _, kdata_item in get_kdata(security_item).iterrows():
            try:
                id = '{}_{}'.format(kdata_item['securityId'], kdata_item['timestamp'])
                kdata = StockKData(meta={'id': id}, id=id)
                fill_doc_type(kdata, json.loads(kdata_item.to_json()))
                kdata.save(index=index_name)
            except Exception as e:
                logger.warn("wrong KdataDay:{},error:{}", kdata_item, e)


def index_kdata_to_es(force=False):
    for _, security_item in get_security_list(security_type='index').iterrows():
        # 创建索引
        index_name = get_es_kdata_index(security_item['id'])
        index_mapping(index_name, IndexKData)

        for _, kdata_item in get_kdata(security_item).iterrows():
            try:
                id = '{}_{}'.format(kdata_item['securityId'], kdata_item['timestamp'])
                kdata = IndexKData(meta={'id': id}, id=id)
                fill_doc_type(kdata, json.loads(kdata_item.to_json()))
                kdata.save(index=index_name, force=force)
            except Exception as e:
                logger.warn("wrong KdataDay:{},error:{}", kdata_item, e)


def balance_sheet_to_es():
    index_mapping('balance_sheet', BalanceSheet)
    for _, security_item in get_security_list().iterrows():
        for json_object in get_balance_sheet_items(security_item):
            try:
                balance_sheet = BalanceSheet(meta={'id': json_object['id']})
                fill_doc_type(balance_sheet, json_object)
                balance_sheet.save()
            except Exception as e:
                logger.warn("wrong BalanceSheet:{},error:{}", json_object, e)


def income_statement_to_es():
    index_mapping('income_statement', IncomeStatement)

    for _, security_item in get_security_list().iterrows():
        for json_object in get_income_statement_items(security_item):
            try:
                income_statement = IncomeStatement(meta={'id': json_object['id']})
                fill_doc_type(income_statement, json_object)
                income_statement.save()
            except Exception as e:
                logger.warn("wrong IncomeStatement:{},error:{}", json_object, e)


def cash_flow_statement_to_es():
    index_mapping('cash_flow_statement', CashFlowStatement)

    for _, security_item in get_security_list().iterrows():
        for json_object in get_cash_flow_statement_items(security_item):
            try:
                cash_flow_statement = CashFlowStatement(meta={'id': json_object['id']})
                fill_doc_type(cash_flow_statement, json_object)
                cash_flow_statement.save()
            except Exception as e:
                logger.warn("wrong CashFlowStatement:{},error:{}", json_object, e)


def forecast_event_to_es():
    for _, security_item in get_security_list().iterrows():
        # 创建索引
        index_name = get_es_forecast_event_index(security_item['id'])
        index_mapping(index_name, ForecastEvent)

        for json_object in get_forecast_items(security_item):
            try:
                forcast_event = ForecastEvent(meta={'id': json_object['id']})
                fill_doc_type(forcast_event, json_object)
                forcast_event.save()
            except Exception as e:
                logger.warn("wrong ForecastEvent:{},error:{}", json_object, e)


if __name__ == '__main__':
    # security_meta_to_es()
    # stock_kdata_to_es()
    index_kdata_to_es(force=True)
    # balance_sheet_to_es()
    # income_statement_to_es()
    # cash_flow_statement_to_es()
    # forecast_event_to_es()
