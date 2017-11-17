import json
import logging

from elasticsearch_dsl import Index

from fooltrader.api.event import get_forecast_items
from fooltrader.api.finance import get_balance_sheet_items, get_income_statement_items, get_cash_flow_statement_items
from fooltrader.api.quote import get_security_list, get_kdata
from fooltrader.contract.es_contract import get_es_kdata_index, get_es_forecast_event_index
from fooltrader.domain.event import ForecastEvent
from fooltrader.domain.finance import BalanceSheet, IncomeStatement, CashFlowStatement
from fooltrader.domain.meta import StockMeta
from fooltrader.domain.technical import BfqDayKData, HfqDayKData
from fooltrader.utils.utils import fill_doc_type

logger = logging.getLogger(__name__)


def index_mapping(index_name, doc_type):
    # 创建索引
    index = Index(index_name)
    index.doc_type(doc_type)

    if not index.exists():
        index.create()
    else:
        index.upgrade()


def security_meta_to_es():
    for _, item in get_security_list().iterrows():
        try:
            stock_meta = StockMeta(meta={'id': item['id']}, id=item['id'], type=item['type'],
                                   exchange=item['exchange'], code=item['code'], listDate=item['listDate'],
                                   name=item['name'])
            stock_meta.save()
        except Exception as e:
            logger.warn("wrong SecurityItem:{},error:{}", item, e)


def kdata_to_es(fuquan='bfq'):
    for _, security_item in get_security_list().iterrows():
        # 创建索引
        index_name = get_es_kdata_index(security_item['id'], fuquan=fuquan)
        if fuquan == 'hfq':
            index_mapping(index_name, HfqDayKData)
        else:
            index_mapping(index_name, BfqDayKData)

        for _, kdata_item in get_kdata(security_item, fuquan=fuquan).iterrows():
            try:
                id = '{}_{}'.format(kdata_item['securityId'], kdata_item['timestamp'])
                if fuquan == 'hfq':
                    kdata = HfqDayKData(
                        meta={'id': id},
                        id=id)
                else:
                    kdata = BfqDayKData(
                        meta={'id': id},
                        id=id)
                fill_doc_type(kdata, json.loads(kdata_item.to_json()))
                kdata.save()
            except Exception as e:
                logger.warn("wrong KdataDay:{},fuquan:{},error:{}", kdata_item, fuquan, e)


def balance_sheet_to_es():
    for security_item in get_security_list():
        for json_object in get_balance_sheet_items(security_item):
            try:
                balance_sheet = BalanceSheet(meta={'id': json_object['id']})
                fill_doc_type(balance_sheet, json_object)
                balance_sheet.save()
            except Exception as e:
                logger.warn("wrong BalanceSheet:{},error:{}", json_object, e)


def income_statement_to_es():
    for security_item in get_security_list():
        for json_object in get_income_statement_items(security_item):
            try:
                income_statement = IncomeStatement(meta={'id': json_object['id']})
                fill_doc_type(income_statement, json_object)
                income_statement.save()
            except Exception as e:
                logger.warn("wrong IncomeStatement:{},error:{}", json_object, e)


def cash_flow_statement_to_es():
    for security_item in get_security_list():
        for json_object in get_cash_flow_statement_items(security_item):
            try:
                cash_flow_statement = CashFlowStatement(meta={'id': json_object['id']})
                fill_doc_type(cash_flow_statement, json_object)
                cash_flow_statement.save()
            except Exception as e:
                logger.warn("wrong CashFlowStatement:{},error:{}", json_object, e)


def forecast_event_to_es():
    for security_item in get_security_list():
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
    from elasticsearch_dsl.connections import connections

    connections.create_connection(hosts=['localhost'], timeout=20)
    kdata_to_es()
    # balance_sheet_to_es()
    # income_statement_to_es()
    # cash_flow_statement_to_es()
    # forecast_event_to_es()
