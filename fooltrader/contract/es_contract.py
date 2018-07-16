# -*- coding: utf-8 -*-

def get_es_kdata_index(security_type='stock', exchange='sh', level='day'):
    # 按 类型_国家_级别 来索引
    if exchange in ['sh', 'sz']:
        return '{}_{}_{}_kdata'.format(security_type, 'china', level)
    elif exchange in ['nasdaq', 'amex', 'nyse']:
        return '{}_{}_{}_kdata'.format(security_type, 'usa', level)
    else:
        return '{}_{}_{}_kdata'.format(security_type, exchange, level)


# one index for stock forecast event
def get_es_finance_forecast_event_index(security_type='stock'):
    return '{}_finance_forecast_event'.format(security_type)


# one index for stock report event
def get_es_finance_report_event_index(security_type='stock'):
    return '{}_finance_report_event'.format(security_type)
