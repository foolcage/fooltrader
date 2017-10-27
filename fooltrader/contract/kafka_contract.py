def get_kafka_tick_topic(security_id):
    return '{}_tick'.format(security_id)


def get_kafka_kdata_topic(security_id, houfuquan=False, level='day', ):
    if houfuquan:
        return '{}_{}_{}_kdata'.format(security_id, "houfuquan", level)
    else:
        return '{}_{}_kdata'.format(security_id, level)
