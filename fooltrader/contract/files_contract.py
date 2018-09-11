# -*- coding: utf-8 -*-

import os
from datetime import datetime

from fooltrader import settings
from fooltrader.utils.time_utils import to_time_str


def get_exchange_dir(security_type='future', exchange='shfe'):
    return os.path.join(settings.FOOLTRADER_STORE_PATH, security_type, exchange)


def get_exchange_trading_calendar_path(security_type='future', exchange='shfe'):
    return os.path.join(get_exchange_dir(security_type, exchange), 'trading_calendar.json')


def get_exchange_cache_dir(security_type='future', exchange='shfe', the_year=None,
                           data_type="day_kdata"):
    if the_year:
        the_dir = os.path.join(settings.FOOLTRADER_STORE_PATH, ".cache", "{}.{}.cache".format(security_type, exchange))
        return os.path.join(the_dir, "{}_{}".format(the_year, data_type))
    return os.path.join(settings.FOOLTRADER_STORE_PATH, ".cache", "{}.{}.cache".format(security_type, exchange))


def get_exchange_cache_path(security_type='future', exchange='shfe', the_date=datetime.today(), data_type="day_kdata"):
    the_dir = get_exchange_cache_dir(security_type=security_type, exchange=exchange, the_year=the_date.year,
                                     data_type=data_type)
    if not os.path.exists(the_dir):
        os.makedirs(the_dir)
    return os.path.join(the_dir, to_time_str(the_time=the_date))


# 标的相关
def get_security_list_path(security_type, exchange):
    return os.path.join(settings.FOOLTRADER_STORE_PATH, security_type, '{}.csv'.format(exchange))


def get_security_dir(security_item=None, security_type=None, exchange=None, code=None):
    if security_type and exchange and code:
        return os.path.join(settings.FOOLTRADER_STORE_PATH, security_type, exchange, code)
    else:
        return os.path.join(settings.FOOLTRADER_STORE_PATH, security_item['type'], security_item['exchange'],
                            security_item['code'])


def get_security_meta_path(security_item=None, security_type=None, exchange=None, code=None):
    return os.path.join(
        get_security_dir(security_item=security_item, security_type=security_type, exchange=exchange, code=code),
        "meta.json")


# k线相关
def adjust_source(security_item, source):
    # 对于使用者，不需要指定source,系统会选择目前质量最好的source
    if not source:
        if security_item['type'] == 'future' or security_item['type'] == 'coin':
            source = 'exchange'
        if security_item['type'] == 'stock' or security_item['type'] == 'index':
            source = '163'
    return source


def get_kdata_dir(security_item, fuquan='bfq'):
    # 目前只有股票需要复权信息
    if security_item['type'] == 'stock':
        return os.path.join(get_security_dir(security_item), 'kdata', _to_valid_fuquan(fuquan))
    else:
        return os.path.join(get_security_dir(security_item), 'kdata')


def get_kdata_path(security_item, source=None, fuquan='bfq', year=None, quarter=None, level='day'):
    source = adjust_source(security_item, source)
    if source == 'sina':
        if not year and not quarter:
            return os.path.join(get_kdata_dir(security_item, fuquan), 'dayk.csv')
        else:
            return os.path.join(get_kdata_dir(security_item, fuquan), '{}Q{}.csv'.format(year, quarter))
    else:
        return os.path.join(get_kdata_dir(security_item, fuquan), '{}_{}k.csv'.format(source, level))


# tick相关
def get_tick_dir(security_item):
    return os.path.join(settings.FOOLTRADER_STORE_PATH, security_item['type'], security_item['exchange'],
                        security_item['code'], 'tick')


def get_tick_path(security_item, date):
    return os.path.join(get_tick_dir(security_item), date + ".csv")


# 事件相关
def get_event_dir(security_item):
    return os.path.join(get_security_dir(security_item), 'event')


def get_event_path(security_item, event_type='finance_forecast'):
    return os.path.join(get_event_dir(security_item), '{}.csv'.format(event_type))


def get_finance_forecast_event_path(security_item):
    return os.path.join(get_event_dir(security_item), 'finance_forecast.csv')


def get_finance_report_event_path(security_item):
    return os.path.join(get_event_dir(security_item), 'finance_report.csv')


# 财务相关
def get_finance_dir(security_item):
    return os.path.join(get_security_dir(security_item), "finance")


# 美股财务数据目前只存一个文件
def get_finance_path(security_item):
    return os.path.join(get_finance_dir(security_item), "finance.csv")


def get_balance_sheet_path(security_item):
    return os.path.join(get_finance_dir(security_item), "balance_sheet.xls")


def get_income_statement_path(security_item):
    return os.path.join(get_finance_dir(security_item), "income_statement.xls")


def get_cash_flow_statement_path(security_item):
    return os.path.join(get_finance_dir(security_item), "cash_flow_statement.xls")


def _to_valid_fuquan(fuquan='bfq'):
    if fuquan == 'qfq' or fuquan == 'hfq':
        return fuquan
    else:
        return 'bfq'


def get_trading_dates_path_163(security_item):
    return os.path.join(get_security_dir(security_item), 'trading_dates_163.json')


def get_trading_dates_path_ths(security_item):
    return os.path.join(get_security_dir(security_item), 'trading_dates_ths.json')


def get_trading_dates_path_sse(security_item):
    return os.path.join(get_security_dir(security_item), 'trading_dates_sse.json')


def get_code_from_path(the_path, security_type='stock'):
    the_dir = os.path.join(settings.FOOLTRADER_STORE_PATH, security_type)
    if the_dir in the_path:
        strs = the_path[len(the_dir):].split('/')
        if len(strs) > 2:
            return strs[2]
