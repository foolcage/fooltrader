from fooltrader.api import quote
from fooltrader.api.quote import get_security_item


def ma(security_id, start, end, level='day', fuquan='bfq', source='sina', window=5,
       col=['close', 'volume', 'turnover']):
    df = quote.get_kdata(security_id, fuquan=fuquan, source=source, level=level)
    # 向前补全计算window
    df1 = df[:start]
    df2 = df1[-window + 1:]
    adjust_start = df2.index[0]

    df_result = df.loc[adjust_start:end, col].rolling(window=window, min_periods=0).mean()[start:end]
    df_result.columns = ["{}_ma{}".format(item, window) for item in col]
    return df_result


def ema(security_id, start, end, level='day', fuquan='bfq', source='sina', window=12, col=['close'], pre_count=0):
    df = quote.get_kdata(security_id, fuquan=fuquan, source=source, level=level)
    # 向前补全计算window
    df1 = df[:start]
    df2 = df1[-window - pre_count + 1:]
    adjust_start = df2.index[0]

    df_result = df.loc[adjust_start:end, col].ewm(span=window, adjust=False).mean()
    if pre_count == 0:
        df_result = df_result[start:end]
    else:
        df_result = df_result[window - 1:]
    df_result.columns = ["{}_ema{}".format(item, window) for item in col]
    return df_result


def macd(security_id, start, end, level='day', fuquan='bfq', source='sina', slow=26, fast=12, n=9, col=['close']):
    ema_fast = ema(security_id, start, end, level, fuquan, window=fast, pre_count=n, col=col)
    ema_fast.columns = ['ema']

    ema_slow = ema(security_id, start, end, level, fuquan, window=slow, pre_count=n, col=col)
    ema_slow.columns = ['ema']

    result = ema_fast - ema_slow
    result['dea'] = result.ewm(span=n, adjust=False).mean()
    result.columns = ['diff', 'dea']
    result['macd'] = (result['diff'] - result['dea']) * 2

    return result[start:end]


if __name__ == '__main__':
    print(ema(get_security_item('000001'), start='20171101', end='20171201', pre_count=9))
    print(ema(get_security_item('000001'), start='20171101', end='20171201'))
    print(macd(get_security_item('000001'), start='20171101', end='20171201', n=9))
