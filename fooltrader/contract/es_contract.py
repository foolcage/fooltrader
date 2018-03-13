# -*- coding: utf-8 -*-

def get_es_kdata_index(security_type='stock', exchange='sh', level='day'):
    if exchange in ['sh', 'sz']:
        return '{}_{}_{}_kdata'.format(security_type, 'china', level)
    elif exchange in ['nasdaq', 'amex', 'nyse']:
        return '{}_{}_{}_kdata'.format(security_type, 'usa', level)


def get_es_forecast_event_index(security_id):
    return '{}_forecast_event'.format(security_id)
