# -*- coding: utf-8 -*-


def get_es_kdata_index(security_type='stock', exchange='sh', level='day'):
    # 按 类型_国家_级别 来索引
    if exchange in ['sh', 'sz']:
        return '{}_{}_{}_kdata'.format(security_type, 'china', level)
    elif exchange in ['nasdaq', 'amex', 'nyse']:
        return '{}_{}_{}_kdata'.format(security_type, 'usa', level)
    else:
        return '{}_{}_{}_kdata'.format(security_type, exchange, level)


def get_es_finance_event_index(event_type='finance_forecast'):
    return '{}_event'.format(event_type)


def get_es_statistic_index(security_type='stock', exchange='sh', level='day'):
    # 按 类型_国家_级别 来索引
    if exchange in ['sh', 'sz']:
        return '{}_{}_{}_statistic'.format(security_type, 'china', level)
    elif exchange in ['nasdaq', 'amex', 'nyse']:
        return '{}_{}_{}_statistic'.format(security_type, 'usa', level)
    else:
        return '{}_{}_{}_statistic'.format(security_type, exchange, level)


def get_cryptocurrency_daily_user_statistic_index(main_chain='eos'):
    return '{}_daily_user_statistic'.format(main_chain)


def get_cryptocurrency_user_statistic_index(main_chain='eos'):
    return '{}_user_statistic'.format(main_chain)
