# -*- coding: utf-8 -*-

"""
这里主要定义各种数据的属性名称，其对应：csv列名，DataFrame的columns,json(dict)的keys,存储到es的fields
"""

# 投资标的
SECURITY_COL = ['code', 'name', 'timestamp', 'listDate', 'exchange', 'type', 'id']

# 代码,名字,上市日期,交易所,类型,id,新浪行业,新浪概念,区域,板块(美股才有),细分行业(美股才有)
STOCK_META_COL = ['code', 'name', 'timestamp', 'listDate', 'exchange', 'type', 'id', 'sinaIndustry', 'sinaConcept',
                  'sinaArea',
                  'sector', 'industry']

# 通用k线
KDATA_COMMON_COL = ['timestamp', 'code', 'name', 'low', 'open', 'close', 'high', 'volume', 'securityId',
                    'preClose', 'change', 'changePct']
# tick
TICK_COL = ['timestamp', 'price', 'volume', 'turnover', 'direction']

# 指数K线
# 日期,代码,名称,最低,开盘,收盘,最高,成交量(股),成交额(元),唯一标识,前收盘,涨跌额,涨跌幅(%),换手率(%),总市值,流通市值,平均PE
KDATA_INDEX_COL = ['timestamp', 'code', 'name', 'low', 'open', 'close', 'high', 'volume', 'turnover', 'securityId',
                   'preClose', 'change', 'changePct', 'turnoverRate', 'tCap', 'mCap', 'pe']

# 个股K线
# 日期,代码,名称,最低,开盘,收盘,最高,成交量(股),成交额(元),唯一标识,前收盘,涨跌额,涨跌幅(%),换手率(%),总市值,流通市值,复权因子
KDATA_STOCK_COL = ['timestamp', 'code', 'name', 'low', 'open', 'close', 'high', 'volume', 'turnover', 'securityId',
                   'preClose', 'change', 'changePct', 'turnoverRate', 'tCap', 'mCap', 'factor']
# 期货K线
# 日期,代码,名称,最低,开盘,收盘,最高,成交量(手),成交额(元),唯一标识,前收盘,涨跌额,涨跌幅(%),持仓量,结算价,前结算,涨跌额(按结算价),涨跌幅(按结算价)
KDATA_FUTURE_COL = ['timestamp', 'code', 'name', 'low', 'open', 'close', 'high', 'volume', 'turnover', 'securityId',
                    'preClose', 'change', 'changePct', 'openInterest', 'settlement', 'preSettlement', 'change1',
                    'changePct1']

# 业绩预告
EVENT_STOCK_FINANCE_FORECAST_COL = ["timestamp", "reportPeriod", "securityId", "type", "description", "preEPS",
                                    "changeStart", "change"]
# 业绩公告
EVENT_STOCK_FINANCE_REPORT_COL = ["timestamp", "reportPeriod", "securityId", "title", "url"]

# ***********************************************************
# 以下为一些中间数据，不会直接使用，只是用来合成最终数据或检验数据质量
# ***********************************************************
KDATA_COLUMN_SINA = ['timestamp', 'code', 'low', 'open', 'close', 'high', 'volume', 'turnover', 'securityId']

KDATA_COLUMN_SINA_FQ = ['timestamp', 'code', 'low', 'open', 'close', 'high', 'volume', 'turnover', 'securityId',
                        'factor']

KDATA_COLUMN_163 = ['timestamp', 'code', 'low', 'open', 'close', 'high', 'volume', 'turnover', 'securityId',
                    'preClose', 'change', 'changePct', 'turnoverRate', 'tCap', 'mCap']

KDATA_INDEX_COLUMN_163 = ['timestamp', 'code', 'low', 'open', 'close', 'high', 'volume', 'turnover', 'securityId',
                          'preClose', 'change', 'changePct']

# 上证交易所,深圳交易所,纳斯达克,纽交所,美国证券交易所
# EXCHANGE_LIST_COL = ['sh', 'sz', 'nasdaq', 'nyse', 'amex']
EXCHANGE_LIST_COL = ['sh', 'sz']

FINANCE_SUMMARY_COL = ["id",
                       "securityId",
                       "code",
                       "reportDate",
                       "shares",
                       "sharesAdjusted",
                       "factor",
                       "totalAssets",
                       "totalCurrentAssets",
                       "totalLiabilities",
                       "totalCurrentLiabilities",
                       "bookValue",
                       "minorityBookValue",
                       "preferredEquity",
                       "goodwill",
                       "longTermBorrowing",
                       "operatingRevenue",
                       "netProfit",
                       "netProfitAttributedToParentCompanyOwner",
                       "EPS",
                       "dilutedEPS",
                       "DPS",
                       "netCashFlowsFromOperatingActivities",
                       "netCashFlowsFromInvesting",
                       "netCashFlowsFromFinancingActivities",
                       "cashChange",
                       "cashAtTheEndOfPeriod",
                       "capitalExpenditures",
                       "price",
                       "priceHigh",
                       "priceLow",
                       "ROE",
                       "ROA",
                       "BVPS",
                       "PB",
                       "PE",
                       "cumulativeDividendsPerShare",
                       "dividendPayoutRatio",
                       "longTermDebtToEquityRatio",
                       "equityToAssetsRatio",
                       "netMargin",
                       "assetTurnover",
                       "freeCashFlowPerShare",
                       "currentRatio"]

CHINA_FUTURE_CODE_MAP_NAME = {'cu': '铜',
                              'al': '铝',
                              'zn': '锌',
                              'pb': '铅',
                              'ni': '镍',
                              'sn': '锡',
                              'au': '黄金',
                              'ag': '白银',
                              'rb': '螺纹钢',
                              'wr': '线材',
                              'hc': '热轧卷板',
                              'fu': '燃料油',
                              'bu': '石油沥青',
                              'ru': '天然橡胶'}


def get_future_name(code):
    simple_code = code[:-4]
    return "{}{}".format(CHINA_FUTURE_CODE_MAP_NAME[simple_code], code[-4:])
