import os

from fooltrader import settings


# new
def get_security_list_path(security_type, exchange):
    return os.path.join(settings.FILES_STORE, security_type, '{}.csv'.format(exchange))


def get_kdata_dir():
    pass

def get_kdata_path(item, year, quarter, fuquan):
    pass
# ===========================
def get_sh_stock_list_path():
    return os.path.join(settings.FILES_STORE, settings.SH_STOCK_FILE)


def get_sz_stock_list_path():
    return os.path.join(settings.FILES_STORE, settings.SZ_STOCK_FILE)


def get_security_dir(item):
    return os.path.join(settings.FILES_STORE, item['type'], item['exchange'], item['code'])


def get_event_dir(item):
    return os.path.join(get_security_dir(item), 'event')


def get_forecast_event_path(item):
    return os.path.join(get_event_dir(item), 'forecast.json')


def get_kdata_dir(item, fuquan=False):
    if fuquan:
        return os.path.join(get_security_dir(item), 'kdata', 'fuquan')
    else:
        return os.path.join(get_security_dir(item), 'kdata')


def get_kdata_path_ths(item, fuquan=False):
    if fuquan:
        return os.path.join(get_security_dir(item), 'ths_fuquan_dayk.json')
    else:
        return os.path.join(get_security_dir(item), 'ths_dayk.json')


def get_kdata_path(item, year, quarter, fuquan):
    if fuquan:
        return os.path.join(get_kdata_dir(item, fuquan), '{}_{}_fuquan_dayk.json'.format(year, quarter))
    else:
        return os.path.join(get_kdata_dir(item), '{}_{}_dayk.json'.format(year, quarter))


def get_trading_dates_path(item):
    return os.path.join(get_security_dir(item), 'trading_dates.json')


def get_trading_dates_path_ths(item):
    return os.path.join(get_security_dir(item), 'trading_dates_ths.json')


def get_trading_dates_path_sse(item):
    return os.path.join(get_security_dir(item), 'trading_dates_sse.json')


def get_tick_dir(item):
    return os.path.join(settings.FILES_STORE, item['type'], item['exchange'], item['code'], 'tick')


def get_tick_path(item, date):
    return os.path.join(get_tick_dir(item), date + ".xls")


def get_finance_dir(item):
    return os.path.join(get_security_dir(item), "finance")


def get_balance_sheet_path(item):
    return os.path.join(get_finance_dir(item), "balance_sheet.xls")


def get_income_statement_path(item):
    return os.path.join(get_finance_dir(item), "income_statement.xls")


def get_cash_flow_statement_path(item):
    return os.path.join(get_finance_dir(item), "cash_flow_statement.xls")
