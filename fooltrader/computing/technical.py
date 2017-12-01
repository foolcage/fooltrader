from fooltrader.api import quote
from fooltrader.api.quote import get_security_item


def ma(security_id, start, end, level='day', fuquan='hfq', window=5):
    df = quote.get_kdata(security_id, fuquan=fuquan)
    #
    df1 = df[:start]
    df2 = df1[-window + 1:]
    adjust_start = df2.index[0]
    return df.loc[adjust_start:end, 'close'].rolling(window=window, min_periods=0).mean()[start:end]


if __name__ == '__main__':
    print(ma(get_security_item('600000'), start='20170101', end='20170501'))
    print(ma(get_security_item('600000'), start='20170101', end='20170501',window=250))
