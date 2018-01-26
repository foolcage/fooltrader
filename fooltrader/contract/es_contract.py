def get_es_kdata_index(security_type='stock', exchange='sh', level='day'):
    if exchange == 'sh' or exchange == 'sz':
        return '{}_{}_{}_kdata'.format(security_type, 'china', level)


def get_es_forecast_event_index(security_id):
    return '{}_forecast_event'.format(security_id)
