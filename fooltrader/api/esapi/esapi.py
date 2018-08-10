# -*- coding: utf-8 -*-
import math

from elasticsearch_dsl import Search

from fooltrader import es_client
from fooltrader.api.technical import to_security_item
from fooltrader.contract.data_contract import KDATA_STOCK_COL, KDATA_FUTURE_COL, KDATA_INDEX_COL, \
    KDATA_COMMON_COL
from fooltrader.contract.es_contract import get_es_kdata_index, get_cryptocurrency_user_statistic_index, \
    get_cryptocurrency_daily_user_statistic_index, get_es_statistic_index
from fooltrader.domain.business.es_subscription import PriceSubscription
from fooltrader.utils.es_utils import es_resp_to_payload
from fooltrader.utils.utils import to_time_str


def es_get_subscription(user_id=None, security_id=None, from_idx=0, size=500):
    s = PriceSubscription.search()
    if user_id:
        s = s.filter('term', userId=user_id)
    if security_id:
        s = s.filter('term', securityId=security_id)

    resp = s[from_idx:from_idx + size].execute()
    return es_resp_to_payload(resp)


def es_get_latest_daily_user_statistic(user_id, main_chain='eos', security_id='cryptocurrency_contract_RAM-EOS'):
    index = get_cryptocurrency_daily_user_statistic_index(main_chain=main_chain)

    s = Search(using=es_client, index=index, doc_type='doc') \
        .filter('term', userId=user_id) \
        .filter('term', securityId=security_id)

    s = s.sort({"timestamp": {"order": "desc"}})
    resp = s[0:1].execute()

    datas = [hit['_source'].to_dict() for hit in resp['hits']['hits']]
    if datas:
        return datas[0]
    return None


def es_get_user_statistic(main_chain='eos', security_id='cryptocurrency_contract_RAM-EOS', user_id=None,
                          start_date=None, end_date=None, from_idx=0, size=100, order='volume'):
    index = get_cryptocurrency_user_statistic_index(main_chain=main_chain)

    # get the user time range statistic
    if user_id and start_date and end_date:
        index = get_cryptocurrency_daily_user_statistic_index(main_chain=main_chain)

        s = Search(using=es_client, index=index, doc_type='doc') \
            .filter('term', userId=user_id) \
            .filter('term', securityId=security_id) \
            .filter('range', timestamp={'gte': start_date, 'lte': end_date})

        s = s.sort({"timestamp": {"order": "asc"}})
    # get the user latest statistic
    elif user_id:
        doc_id = '{}_{}'.format(user_id, security_id)
        return es_client.get_source(index=index, doc_type='doc', id=doc_id, ignore=404)
    # get top 100 user latest statistic
    else:
        s = Search(using=es_client, index=index, doc_type='doc') \
            .filter('term', securityId=security_id)

        s = s.sort({order: {"order": "desc"}})

    resp = s[from_idx:from_idx + size].execute()

    return es_resp_to_payload(resp)


def es_get_accounts(main_chain='eos', user_id=None, start_vol=None, end_vol=None, from_idx=0, size=100,
                    order='totalEos', fields=None):
    index = '{}_account'.format(main_chain)

    if not fields:
        fields = ['id', 'timestamp', 'updateTimestamp', 'userId', 'totalEos', 'liquidEos', 'stackedEos',
                  'unstackingEos']

    if user_id:
        s = Search(using=es_client, index=index, doc_type='doc') \
            .filter('term', userId=user_id)
    elif start_vol and end_vol:
        range = {order: {'gte': start_vol, 'lt': end_vol}}
        s = Search(using=es_client, index=index, doc_type='doc') \
            .source(include=fields) \
            .filter('range', **range)
        s = s.sort({order: {"order": "desc"}})
    else:
        s = Search(using=es_client, index=index, doc_type='doc').source(include=fields)
        s = s.sort({order: {"order": "desc"}})

    resp = s[from_idx:from_idx + size].execute()

    return es_resp_to_payload(resp)


def es_get_kdata(security_item, exchange=None, the_date=None, start_date=None, end_date=None, level='day', fields=None,
                 from_idx=0, size=500, csv=False):
    """
    get kdata.

    Parameters
    ----------
    security_item : SecurityItem or str
        the security item,id or code
    exchange : str
        the exchange,set this for cryptocurrency
    the_date : TimeStamp str or TimeStamp
        get the kdata for the exact date
    start_date : TimeStamp str or TimeStamp
        start date
    end_date : TimeStamp str or TimeStamp
        end date
    level : str or int
        the kdata level,{1,5,15,30,60,'day','week','month'},default : 'day'
    fields : filed list for es _source
        if not set,would use the default fields for the security type
    from_idx : int
        pagination start offset
    size : int
        pagination return size

    Returns
    -------
    JSON

    """
    security_item = to_security_item(security_item, exchange)

    index = get_es_kdata_index(security_type=security_item['type'], exchange=security_item['exchange'],
                               level=level)
    if not fields:
        if security_item['type'] == 'stock':
            fields = KDATA_STOCK_COL
        elif security_item['type'] == 'future':
            fields = KDATA_FUTURE_COL
        elif security_item['type'] == 'index':
            fields = KDATA_INDEX_COL
        else:
            fields = KDATA_COMMON_COL

    # 单日的日k线直接按id获取
    if level == 'day' and the_date:
        doc_id = '{}_{}'.format(security_item['id'], to_time_str(the_date))
        return es_client.get_source(index=index, doc_type='doc', id=doc_id, _source_include=fields)
    elif start_date and end_date:
        s = Search(using=es_client, index=index, doc_type='doc') \
            .source(include=fields) \
            .filter('term', code=security_item['code']) \
            .filter('range', timestamp={'gte': start_date, 'lte': end_date}) \
            .sort({"timestamp": {"order": "asc"}})

        resp = s[from_idx:from_idx + size].execute()

        return es_resp_to_payload(resp, csv)


def es_get_statistic(security_item, the_date=None, start_date=None, end_date=None, level='day',
                     from_idx=0, size=500):
    security_item = to_security_item(security_item)

    index = get_es_statistic_index(security_type=security_item['type'], exchange=security_item['exchange'],
                                   level=level)
    # 单日的日k线直接按id获取
    if level == 'day' and the_date:
        doc_id = '{}_{}'.format(security_item['id'], to_time_str(the_date))
        return es_client.get_source(index=index, doc_type='doc', id=doc_id)
    elif start_date and end_date:
        s = Search(using=es_client, index=index, doc_type='doc') \
            .filter('term', code=security_item['code']) \
            .filter('range', timestamp={'gte': start_date, 'lte': end_date}) \
            .sort({"timestamp": {"order": "asc"}})

        resp = s[from_idx:from_idx + size].execute()

        return es_resp_to_payload(resp)


if __name__ == '__main__':
    print(es_get_kdata('300027', the_date='2017-09-04'))
    print(es_get_kdata('300027', the_date='2017-09-04', fields=['close']))
    kdata = es_get_kdata('300028', start_date='2017-09-04', end_date='2017-12-31', from_idx=0, size=10)

    for item in kdata['hits']:
        print(item)
    steps = math.ceil(kdata['total'] / 10)
    for i in range(1, steps + 1):
        the_data = es_get_kdata('300028', start_date='2017-09-04', end_date='2017-12-31', from_idx=i * 10)
        for item in the_data['hits']:
            print(item)
