def get_kafka_tick_topic(security_id):
    return '{}_tick'.format(security_id)


def get_kafka_kdata_topic(security_id, level='day'):
    return '{}_{}_kdata'.format(security_id, level)


def get_es_kdata_index(security_id, level='day', adjust=None):
    if not adjust:
        return '{}_{}_kdata'.format(security_id, level)
    else:
        return '{}_{}_{}_kdata'.format(security_id, adjust, level)


def get_es_forecast_event_index(security_id):
    return '{}_forecast_event'.format(security_id)
