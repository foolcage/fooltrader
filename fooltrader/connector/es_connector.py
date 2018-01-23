import json
import logging
from ast import literal_eval

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
            start_date = latest_record['latestDate']

    for _, item in get_security_list(mode='es', start_date=start_date).iterrows():
        try:
            stock_meta = StockMeta(meta={'id': item['id']})
            fill_doc_type(stock_meta, json.loads(item.to_json()))
            stock_meta.save(force=force)
        except Exception as e:
            logger.warn("wrong SecurityItem:{},error:{}", item, e)


def stock_kdata_to_es(start='000001', end='666666', force=False):
    for _, security_item in get_security_list(start=start, end=end).iterrows():
        # 创建索引
        index_name = get_es_kdata_index(security_item['id'])
        es_index_mapping(index_name, StockKData)

        start_date = None
        if not force:
            latest_record = es_get_latest_record(index_name)
            logger.info("latest_record:{}".format(latest_record))
            if latest_record:
                start_date = latest_record['timestamp']

        for _, kdata_item in get_kdata(security_item, start=start_date).iterrows():
            try:
                id = '{}_{}'.format(kdata_item['securityId'], kdata_item['timestamp'])
                kdata = StockKData(meta={'id': id}, id=id)
                fill_doc_type(kdata, json.loads(kdata_item.to_json()))
                kdata.save(index=index_name, force=force)
            except Exception as e:
                logger.warn("wrong KdataDay:{},error:{}", kdata_item, e)


def index_kdata_to_es(force=False):
    for _, security_item in get_security_list(security_type='index').iterrows():
        # 创建索引
        index_name = get_es_kdata_index(security_item['id'])
        es_index_mapping(index_name, IndexKData)

        start_date = None
        if not force:
            latest_record = es_get_latest_record(index_name)
            logger.info("latest_record:{}".format(latest_record))
            if latest_record:
                start_date = latest_record['timestamp']

        for _, kdata_item in get_kdata(security_item, start=start_date).iterrows():
            try:
                id = '{}_{}'.format(kdata_item['securityId'], kdata_item['timestamp'])
                kdata = IndexKData(meta={'id': id}, id=id)
                fill_doc_type(kdata, json.loads(kdata_item.to_json()))
                kdata.save(index=index_name, force=force)
            except Exception as e:
                logger.warn("wrong KdataDay:{},error:{}", kdata_item, e)


def balance_sheet_to_es(force=False):
    es_index_mapping('balance_sheet', BalanceSheet)
    for _, security_item in get_security_list().iterrows():
        try:
            start_date = None
            if not force:
                latest_record = es_get_latest_record('balance_sheet')
                logger.info("latest_record:{}".format(latest_record))
                if latest_record:
                    start_date = latest_record['reportDate']

            for json_object in get_balance_sheet_items(security_item, start=start_date):
                balance_sheet = BalanceSheet(meta={'id': json_object['id']})
                fill_doc_type(balance_sheet, json_object)
                balance_sheet.save()
        except Exception as e:
            logger.warn("wrong BalanceSheet:{},error:{}", security_item, e)


def income_statement_to_es(force=False):
    es_index_mapping('income_statement', IncomeStatement)

    for _, security_item in get_security_list().iterrows():
        try:
            start_date = None
            if not force:
                latest_record = es_get_latest_record('balance_sheet')
                logger.info("latest_record:{}".format(latest_record))
                if latest_record:
                    start_date = latest_record['reportDate']

            for json_object in get_income_statement_items(security_item, start=start_date):
                income_statement = IncomeStatement(meta={'id': json_object['id']})
                fill_doc_type(income_statement, json_object)
                income_statement.save()
        except Exception as e:
            logger.warn("wrong IncomeStatement:{},error:{}", security_item, e)


def cash_flow_statement_to_es(force=False):
    es_index_mapping('cash_flow_statement', CashFlowStatement)

    for _, security_item in get_security_list().iterrows():
        try:
            start_date = None
            if not force:
                latest_record = es_get_latest_record('balance_sheet')
                logger.info("latest_record:{}".format(latest_record))
                if latest_record:
                    start_date = latest_record['reportDate']

            for json_object in get_cash_flow_statement_items(security_item, start=start_date):
                cash_flow_statement = CashFlowStatement(meta={'id': json_object['id']})
                fill_doc_type(cash_flow_statement, json_object)
                cash_flow_statement.save()
        except Exception as e:
            logger.warn("wrong CashFlowStatement:{},error:{}", security_item, e)


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
    stock_kdata_to_es(start='000338',end='000338')
    # stock_kdata_to_es(force=True)
    # balance_sheet_to_es()
    # income_statement_to_es()
    # cash_flow_statement_to_es()
    # forecast_event_to_es()
