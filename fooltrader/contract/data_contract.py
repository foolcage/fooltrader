# -*- coding: utf-8 -*-

SECURITY_COLUMN = ['code', 'name', 'listDate', 'exchange', 'type', 'id']

KDATA_COLUMN = ['timestamp', 'code', 'low', 'open', 'close', 'high', 'volume', 'turnover', 'securityId']

KDATA_COLUMN_FQ = ['timestamp', 'code', 'low', 'open', 'close', 'high', 'volume', 'turnover', 'securityId', 'factor']

TICK_COLUNM = ['timestamp', 'price', 'volume', 'turnover', 'direction']
KDATA_COLUMN_163 = ['timestamp', 'code', 'low', 'open', 'close', 'high', 'volume', 'turnover', 'securityId',
                    'preClose', 'change', 'changePct', 'turnoverRate', 'tCap', 'mCap']

KDATA_INDEX_COLUMN_163 = ['timestamp', 'code', 'low', 'open', 'close', 'high', 'volume', 'turnover', 'securityId',
                          'preClose', 'change', 'changePct']

# 上证交易所,深圳交易所,纳斯达克,纽交所,美国证券交易所
EXCHANGE_LIST_COL = ['sh', 'sz', 'nasdaq', 'nyse', 'amex']

# 日期,代码,名称,最低,开盘,收盘,最高,成交量(股),成交额(元),唯一标识,前收盘,涨跌额,涨跌幅(%),换手率(%),总市值,流通市值,平均PE
KDATA_COLUMN_INDEX = ['timestamp', 'code', 'name', 'low', 'open', 'close', 'high', 'volume', 'turnover', 'securityId',
                      'preClose', 'change', 'changePct', 'turnoverRate', 'tCap', 'mCap', 'pe']
# 日期,代码,名称,最低,开盘,收盘,最高,成交量(股),成交额(元),唯一标识,前收盘,涨跌额,涨跌幅(%),换手率(%),总市值,流通市值,复权因子
KDATA_COLUMN_STOCK = ['timestamp', 'code', 'name', 'low', 'open', 'close', 'high', 'volume', 'turnover', 'securityId',
                      'preClose', 'change', 'changePct', 'turnoverRate', 'tCap', 'mCap', 'factor']
# 日期,代码,名称,最低,开盘,收盘,最高,成交量(手),成交额(元),唯一标识,前收盘,涨跌额,涨跌幅(%),持仓量,结算价,前结算,涨跌额(按结算价),涨跌幅(按结算价)
KDATA_COLUMN_FUTURE = ['timestamp', 'code', 'name', 'low', 'open', 'close', 'high', 'volume', 'turnover', 'securityId',
                       'preClose', 'change', 'changePct', 'openInterest', 'settlement', 'preSettlement', 'change1',
                       'changePct1']

# 代码,名字,上市日期,交易所,类型,id,新浪行业,新浪概念,区域,板块(美股才有),细分行业(美股才有)
STOCK_META_COL = ['code', 'name', 'listDate', 'exchange', 'type', 'id', 'sinaIndustry', 'sinaConcept', 'sinaArea',
                  'sector', 'industry']

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
