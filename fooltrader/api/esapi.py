# -*- coding: utf-8 -*-
import math

from fooltrader import es
from fooltrader.api.quote import to_security_item
from fooltrader.contract.data_contract import KDATA_COLUMN_STOCK
from fooltrader.contract.es_contract import get_es_kdata_index
from fooltrader.utils.es_utils import es_query_date_range
from fooltrader.utils.utils import to_time_str


def get_kdata(security_item, the_date=None, start_date=None, end_date=None, level='day', fields=KDATA_COLUMN_STOCK,
              from_idx=0, size=10):
    """
    get kdata.

    Parameters
    ----------
    security_item : SecurityItem or str
        the security item,id or code
    the_date : TimeStamp str or TimeStamp
        get the kdata for the exact date
    start_date : TimeStamp str or TimeStamp
        start date
    end_date : TimeStamp str or TimeStamp
        end date
    level : str or int
        the kdata level,{1,5,15,30,60,'day','week','month'},default : 'day'
    from_idx : int
        pagination start offset
    size : int
        pagination return size

    Returns
    -------
    JSON

    """
    security_item = to_security_item(security_item)

    # 单日的日k线直接按id获取
    index = get_es_kdata_index(security_type=security_item['type'], exchange=security_item['exchange'],
                               level=level)
    if not fields:
        return None

    if 'factor' not in fields:
        fields.append('factor')

    if level == 'day' and the_date:
        id = '{}_{}'.format(security_item['id'], to_time_str(the_date))
        return es.get_source(index=index, doc_type='doc', id=id, _source_include=fields)
    elif start_date and end_date:
        query_json = es_query_date_range(start_date, end_date, code=security_item['code'])

        resp = es.search(index=index, doc_type='doc', _source_include=fields,
                         body=query_json, from_=from_idx, size=size,
                         sort='timestamp:asc')
        return resp['hits']


if __name__ == '__main__':
    print(get_kdata('300027', the_date='2017-09-04'))
    print(get_kdata('300027', the_date='2017-09-04', fields=['close']))
    kdata = get_kdata('300028', start_date='2017-09-04', end_date='2017-12-31', from_idx=0, size=10)

    for item in kdata['hits']:
        print(item)
    steps = math.ceil(kdata['total'] / 10)
    for i in range(1, steps + 1):
        the_data = get_kdata('300028', start_date='2017-09-04', end_date='2017-12-31', from_idx=i * 10)
        for item in the_data['hits']:
            print(item)
