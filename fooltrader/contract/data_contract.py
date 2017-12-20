SECURITY_COLUMN = ['code', 'name', 'listDate', 'exchange', 'type', 'id']

KDATA_COLUMN = ['timestamp', 'code', 'low', 'open', 'close', 'high', 'volume', 'turnover', 'securityId']

KDATA_COLUMN_FQ = ['timestamp', 'code', 'low', 'open', 'close', 'high', 'volume', 'turnover', 'securityId', 'factor']

TICK_COLUNM = ['timestamp', 'price', 'volume', 'turnover', 'direction']

# 日期,代码,最低,开盘,收盘,最高,成交量(股),成交额(元),唯一标识,前收盘,涨跌额,涨跌幅(%),换手率(%),总市值,流通市值,复权因子
KDATA_COLUMN_FULL = ['timestamp', 'code', 'low', 'open', 'close', 'high', 'volume', 'turnover', 'securityId',
                     'preClose', 'change', 'changePct', 'turnoverRate', 'tCap', 'mCap', 'factor']

KDATA_COLUMN_163 = ['timestamp', 'code', 'low', 'open', 'close', 'high', 'volume', 'turnover', 'securityId',
                    'preClose', 'change', 'changePct', 'turnoverRate', 'tCap', 'mCap']
