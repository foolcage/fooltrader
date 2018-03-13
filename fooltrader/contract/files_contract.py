# -*- coding: utf-8 -*-

import os

from fooltrader import settings


# 分类相关
def get_category_path(security_type='stock', classified='industry', source='sina', category_item=None):
    if category_item:
        return os.path.join(get_category_dir(security_type), '{}_{}_{}.csv'.format(source, classified, category_item))
    else:
        return os.path.join(get_category_dir(security_type), '{}_{}.csv'.format(source, classified))


def get_category_dir(security_type='stock'):
    return os.path.join(settings.FOOLTRADER_STORE_PATH, security_type, 'category')


# 标的相关
def get_security_list_path(security_type, exchange):
    return os.path.join(settings.FOOLTRADER_STORE_PATH, security_type, '{}.csv'.format(exchange))


def get_security_dir(item):
    return os.path.join(settings.FOOLTRADER_STORE_PATH, item['type'], item['exchange'], item['code'])


# k线相关
def get_kdata_dir(item, fuquan='bfq'):
    if item['type'] == 'index':
        return os.path.join(get_security_dir(item), 'kdata')
    elif item['type'] == 'stock':
        return os.path.join(get_security_dir(item), 'kdata', _to_valid_fuquan(fuquan))


def get_kdata_path(item, source='163', fuquan='bfq', year=None, quarter=None):
    if source == 'sina':
        if not year and not quarter:
            return os.path.join(get_kdata_dir(item, fuquan), 'dayk.csv')
        else:
            return os.path.join(get_kdata_dir(item, fuquan), '{}Q{}.csv'.format(year, quarter))
    else:
        return os.path.join(get_kdata_dir(item, fuquan), '{}_dayk.csv'.format(source))


# tick相关
def get_tick_dir(item):
    return os.path.join(settings.FOOLTRADER_STORE_PATH, item['type'], item['exchange'], item['code'], 'tick')


def get_tick_path(item, date):
    return os.path.join(get_tick_dir(item), date + ".csv")


# 事件相关
def get_event_dir(item):
    return os.path.join(get_security_dir(item), 'event')


def get_forecast_event_path(item, event='forecast'):
    return os.path.join(get_event_dir(item), '{}.json'.format(event))


def get_event_path(item, event='finance_report'):
    return os.path.join(get_event_dir(item), '{}.csv'.format(event))


# 财务相关
def get_finance_dir(item):
    return os.path.join(get_security_dir(item), "finance")


# 美股财务数据目前只存一个文件
def get_finance_path(item):
    return os.path.join(get_finance_dir(item), "finance.csv")


def get_balance_sheet_path(item):
    return os.path.join(get_finance_dir(item), "balance_sheet.xls")


def get_income_statement_path(item):
    return os.path.join(get_finance_dir(item), "income_statement.xls")


def get_cash_flow_statement_path(item):
    return os.path.join(get_finance_dir(item), "cash_flow_statement.xls")


def _to_valid_fuquan(fuquan='bfq'):
    if fuquan == 'qfq' or fuquan == 'hfq':
        return fuquan
    else:
        return 'bfq'


def get_trading_dates_path_163(item):
    return os.path.join(get_security_dir(item), 'trading_dates_163.json')


def get_trading_dates_path_ths(item):
    return os.path.join(get_security_dir(item), 'trading_dates_ths.json')


def get_trading_dates_path_sse(item):
    return os.path.join(get_security_dir(item), 'trading_dates_sse.json')
