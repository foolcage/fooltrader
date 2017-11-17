def get_es_kdata_index(security_id, level='day', fuquan='hfq'):
    if fuquan == 'qfq' or fuquan == 'hfq':
        return '{}_{}_{}_kdata'.format(security_id, fuquan, level)
    else:
        return '{}_{}_{}_kdata'.format(security_id, 'bfq', level)


def get_es_forecast_event_index(security_id):
    return '{}_forecast_event'.format(security_id)
