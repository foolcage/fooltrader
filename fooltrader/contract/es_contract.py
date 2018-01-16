def get_es_kdata_index(security_id, level='day'):
    return '{}_{}_kdata'.format(security_id, level)


def get_es_forecast_event_index(security_id):
    return '{}_forecast_event'.format(security_id)
