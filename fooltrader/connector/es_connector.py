# -*- coding: utf-8 -*-

import json
import logging

import elasticsearch.helpers
import pandas as pd

from fooltrader import es_client
from fooltrader.api.event import get_finance_forecast_event, get_finance_report_event
from fooltrader.api.fundamental import get_balance_sheet_items, get_income_statement_items, \
    get_cash_flow_statement_items, \
    get_finance_summary_items
from fooltrader.api.technical import get_security_list, get_kdata
from fooltrader.consts import CRYPTOCURRENCY_CODE
from fooltrader.contract.es_contract import get_es_kdata_index
from fooltrader.domain.data.es_event import FinanceForecastEvent, FinanceReportEvent
from fooltrader.domain.data.es_finance import BalanceSheet, IncomeStatement, CashFlowStatement, FinanceSummary
from fooltrader.domain.data.es_quote import StockMeta, StockKData, IndexKData, CryptoCurrencyKData, IndexMeta, \
    CryptocurrencyMeta
from fooltrader.settings import US_STOCK_CODES
from fooltrader.utils.es_utils import es_index_mapping, es_get_latest_timestamp
from fooltrader.utils.utils import fill_doc_type, index_df_with_time

logger = logging.getLogger(__name__)


# we make the data always have these fields:id,timestamp,securityId
# so we could handle append data to index in uniform way
def df_to_es(df, doc_type, index_name=None, timestamp_filed='timestamp', security_item=None, force=False):
    if not index_name:
        index_name = doc_type().meta.index

    es_index_mapping(index_name, doc_type)

    if not force:
        query = None
        if not force:
            query = {
                "term": {"securityId": ""}
            }
            query["term"]["securityId"] = security_item["id"]

        start_date = es_get_latest_timestamp(index=index_name, query=query, time_field=timestamp_filed)
        logger.info("{} latest timestamp:{}".format(index_name, start_date))
        if start_date:
            df = df.loc[start_date:, :]

    actions = []

    for _, item in df.iterrows():
        try:
            es_data = doc_type(meta={'id': item['id'], 'index': index_name})

            item_json = json.loads(item.to_json())

            fill_doc_type(es_data, item_json)

            actions.append(es_data.to_dict(include_meta=True))
        except Exception as e:
            logger.exception("wrong item:{},error:{}".format(item, e))

    if actions:
        resp = elasticsearch.helpers.bulk(es_client, actions)
        logger.info("index to {} success:{} failed:{}".format(index_name, resp[0], len(resp[1])))
        if resp[1]:
            logger.error("index to {} error:{}".format(index_name, resp[1]))


def security_meta_to_es(security_type='stock'):
    if security_type == 'stock':
        doc_type = StockMeta
    elif security_type == 'cryptocurrency':
        doc_type = CryptocurrencyMeta
    elif security_type == 'index':
        doc_type = IndexMeta

    df = get_security_list(security_type=security_type, mode='es')

    df_to_es(df, doc_type, force=True)


def kdata_to_es(security_type='stock', start_code=None, end_code=None, force=False):
    codes = None
    if security_type == 'stock':
        doc_type = StockKData
    elif security_type == 'index':
        doc_type = IndexKData
    elif security_type == 'cryptocurrency':
        doc_type = CryptoCurrencyKData
        codes = CRYPTOCURRENCY_CODE

    for _, security_item in get_security_list(security_type=security_type, start_code=start_code,
                                              end_code=end_code, codes=codes).iterrows():
        index_name = get_es_kdata_index(security_item['type'], security_item['exchange'])

        df = get_kdata(security_item, generate_id=True)

        df_to_es(df, doc_type=doc_type, index_name=index_name, security_item=security_item, force=force)


def finance_sheet_to_es(sheet_type=None, start_code=None, end_code=None, force=False):
    if sheet_type is None:
        sheet_types = ['balance_sheet', 'income_statement', 'cash_flow_statement']
    else:
        sheet_types = [sheet_type]

    for sheet_type in sheet_types:
        if sheet_type == 'balance_sheet':
            doc_type = BalanceSheet
        elif sheet_type == 'income_statement':
            doc_type = IncomeStatement
        elif sheet_type == 'cash_flow_statement':
            doc_type = CashFlowStatement

        es_index_mapping(sheet_type, doc_type)

        for _, security_item in get_security_list(start_code=start_code, end_code=end_code).iterrows():
            try:
                if sheet_type == 'balance_sheet':
                    items = get_balance_sheet_items(security_item)
                elif sheet_type == 'income_statement':
                    items = get_income_statement_items(security_item)
                elif sheet_type == 'cash_flow_statement':
                    items = get_cash_flow_statement_items(security_item)

                df = pd.DataFrame(items)

                df = index_df_with_time(df, index='reportPeriod')

                df_to_es(df, doc_type=doc_type, timestamp_filed='reportPeriod', security_item=security_item,
                         force=force)
            except Exception as e:
                logger.exception("index {} {} failed".format(security_item['code'], sheet_type), e)


def usa_stock_finance_to_es(force=False):
    for _, security_item in get_security_list(security_type='stock', exchanges=['nasdaq'],
                                              codes=US_STOCK_CODES).iterrows():
        df = get_finance_summary_items(security_item)

        df_to_es(df, doc_type=FinanceSummary, timestamp_filed='reportPeriod', security_item=security_item, force=force)


def finance_event_to_es(event_type='finance_forecast', start_code=None, end_code=None, force=False):
    if event_type == 'finance_forecast':
        doc_type = FinanceForecastEvent
    elif event_type == 'finance_report':
        doc_type = FinanceReportEvent

    for _, security_item in get_security_list(start_code=start_code, end_code=end_code).iterrows():
        if event_type == 'finance_forecast':
            df = get_finance_forecast_event(security_item)
        elif event_type == 'finance_report':
            df = get_finance_report_event(security_item)

        df_to_es(df, doc_type=doc_type, security_item=security_item, force=force)


if __name__ == '__main__':
    kdata_to_es(security_type='cryptocurrency')
    # security_meta_to_es()
    # kdata_to_es(start_code='300027', end_code='300028', force=False)
    # kdata_to_es(security_type='index', force=True)
    # finance_sheet_to_es('balance_sheet', start_code='300027', end_code='300028', force=False)
    # finance_sheet_to_es('income_statement', start_code='300027', end_code='300028', force=False)
    # finance_sheet_to_es('cash_flow_statement', start_code='300027', end_code='300028', force=False)
    # finance_event_to_es(start_code='300027', end_code='300028', force=False)
    # finance_event_to_es(event_type='finance_report', start_code='300027', end_code='300028', force=False)
