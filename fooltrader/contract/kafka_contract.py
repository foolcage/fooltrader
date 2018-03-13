# -*- coding: utf-8 -*-

def get_kafka_tick_topic(security_id):
    return '{}_tick'.format(security_id)


def get_kafka_kdata_topic(security_id, fuquan="hfq", level='day'):
    if fuquan == 'qfq' or fuquan == 'hfq':
        return '{}_{}_{}_kdata'.format(security_id, fuquan, level)
    else:
        return '{}_{}_{}_kdata'.format(security_id, 'bfq', level)
