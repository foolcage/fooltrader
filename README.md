[![Build Status](https://travis-ci.org/foolcage/fooltrader.svg?branch=master)](https://travis-ci.org/foolcage/fooltrader)

**Read this in other languages: [English](README-en.md).**  
# fooltrader:trade as a fool
>"要在市场上生存，就必须远离聪明，因为，你的聪明在市场面前一钱不值"------缠中说禅  

fooltrader是一个利用*大数据*技术设计的*量化分析交易系统*,包括数据的抓取,清洗,结构化,计算,展示,回测和交易.  
它的目标是提供一个统一的框架来对*全市场*(股票,期货,债券,外汇,数字货币,宏观经济等)进行研究,回测,预测,交易.  
它的适用对象包括:***量化交易员,财经类专业师生,对经济数据感兴趣的人,程序员,喜欢自由而有探索精神的人***  

# 1. 能做什么
## 1.1 **自定义分析逻辑和视图**  
![](./screenshots/profit_price.gif)
>输入你感兴趣的个股,查看其净利润跟股价的关系.  

![](./screenshots/analyze1.png)  
>聚合展示你关心的视图  

[*更多例子*](./docs/kibana-analyze.md)

## 1.2 **免费数据源和精心分类的统一api**  

api输出结果具体字段含义请参考[*数据协议*](./docs/contract.md).  
### A股数据 ###
```bash
In [1]:import fooltrader as ft
In [2]:ft.get_kdata('000778')
#试一试
#ft.get_kdata('300027',start_date='20170630',end_date='20170715')
#ft.get_kdata('300027',start_date='20170630',end_date='20170715')

timestamp    code  name    low   open  close   high    volume      turnover       securityId    ...             mCap  factor  hfqClose   hfqOpen   hfqHigh    hfqLow  qfqClose   qfqOpen   qfqHigh    qfqLow
timestamp                                                                                                    ...                                                                                                         
1997-06-06  1997-06-06  000778  新兴铸管  18.00  18.10  19.68  20.70  45335789  8.904533e+08  stock_sz_000778    ...     1.416960e+09   1.000  19.68000  18.10000  20.70000  18.00000  1.497375  1.377159  1.574983  1.369550
1997-06-09  1997-06-09  000778  新兴铸管  18.00  20.00  18.51  20.44  11333248  2.148290e+08  stock_sz_000778    ...     1.332720e+09   1.000  18.51000  20.00000  20.44000  18.00000  1.408354  1.521723  1.555200  1.369550
1997-06-10  1997-06-10  000778  新兴铸管  16.66  18.50  16.75  18.60   6641283  1.155679e+08  stock_sz_000778    ...     1.206000e+09   1.000  16.75000  18.50000  18.60000  16.66000  1.274443  1.407593  1.415202  1.267595
1997-06-11  1997-06-11  000778  新兴铸管  15.90  16.60  17.35  17.40   5560642  9.365633e+07  stock_sz_000778    ...     1.249200e+09   1.000  17.35000  16.60000  17.40000  15.90000  1.320094  1.263030  1.323899  1.209769
1997-06-12  1997-06-12  000778  新兴铸管  16.80  17.68  16.80  17.70   3022235  5.142033e+07  stock_sz_000778    ...     1.209600e+09   1.000  16.80000  17.68000  17.70000  16.80000  1.278247  1.345203  1.346724  1.278247
```
### 期货数据 ###
```bash
In [3]:ft.get_kdata('rb1601')
           timestamp    code   name     low    open   close    high    volume     turnover          securityId  preClose  change  changePct  openInterest  settlement  preSettlement  change1  changePct1
timestamp                                                                                                                                                                                                
2015-01-16  20150116  rb1601  螺纹钢rb  2533.0  2545.0  2550.0  2568.0      96.0      244.468  future_shfe_rb1601    2518.0    32.0   0.012708          66.0      2546.0         2518.0     28.0    0.011120
2015-01-19  20150119  rb1601  螺纹钢rb  2515.0  2534.0  2541.0  2558.0     486.0     1231.174  future_shfe_rb1601    2550.0    -5.0  -0.001961         212.0      2533.0         2546.0    -13.0   -0.005106
2015-01-20  20150120  rb1601  螺纹钢rb  2521.0  2554.0  2529.0  2554.0     134.0      339.290  future_shfe_rb1601    2541.0    -4.0  -0.001574         286.0      2532.0         2533.0     -1.0   -0.000395
2015-01-21  20150121  rb1601  螺纹钢rb  2516.0  2520.0  2516.0  2540.0     294.0      743.266  future_shfe_rb1601    2529.0   -16.0  -0.006327         410.0      2528.0         2532.0     -4.0   -0.001580
2015-01-22  20150122  rb1601  螺纹钢rb  2515.0  2519.0  2521.0  2530.0     310.0      782.114  future_shfe_rb1601    2516.0    -7.0  -0.002782         576.0      2522.0         2528.0     -6.0   -0.002373

```
### 数字货币 ###
```bash
In [4]: ft.get_kdata('BTC-USD',exchange='kraken')

             timestamp     code     name     low    open   close    high       volume                     securityId  preClose  change  changePct
timestamp                                                                                                                                        
2016-07-08  2016-07-08  BTC-USD  BTC/USD   634.0   640.4   671.4   671.4  1651.592635  cryptocurrency_kraken_BTC-USD       NaN     NaN        NaN
2016-07-09  2016-07-09  BTC-USD  BTC/USD   622.0   671.9   652.0   671.9  1908.295953  cryptocurrency_kraken_BTC-USD     671.4   -19.4  -0.029755
2016-07-10  2016-07-10  BTC-USD  BTC/USD   642.4   652.0   650.0   655.6   429.290787  cryptocurrency_kraken_BTC-USD     652.0    -2.0  -0.003077
2016-07-11  2016-07-11  BTC-USD  BTC/USD   645.3   652.5   650.7   663.3   814.157258  cryptocurrency_kraken_BTC-USD     650.0     0.7   0.001076
2016-07-12  2016-07-12  BTC-USD  BTC/USD   647.1   650.7   666.0   675.9   923.800268  cryptocurrency_kraken_BTC-USD     650.7    15.3   0.022973

```
### tick ###
```
In [5]: for item in ft.get_ticks('000338'):
    ...:     print(item)
```
![](./screenshots/tick.gif)

### 基本面数据 ###
```bash
In [5]: ft.get_income_statement_items('300027',report_period='2017-06-30')
#试一试
#ft.get_balance_sheet_items('300027',,report_event_date='2017-01-01')
#ft.get_cash_flow_statement_items('300027')
Out[2]:
{'EPS': 0.15,
 'ManagingCosts': 257005115.85,
 'accumulatedOtherComprehensiveIncome': 471486112.3,
 'assetsDevaluation': -21647912.31,
 'attributableToMinorityShareholders': 90255906.93,
 'attributableToOwnersOfParentCompany': 381230205.37,
 'businessTaxesAndSurcharges': 80033207.21,
 'code': '300027',
 'dilutedEPS': 0.15,
 'disposalLossOnNonCurrentLiability': 281050.25,
 'exchangeGains': 0.0,
 'financingExpenses': 132202866.43,
 'id': 'stock_sz_300027_20170630',
 'incomeFromChangesInFairValue': 0.0,
 'incomeTaxExpense': 111864455.56,
 'investmentIncome': 541478955.17,
 'investmentIncomeFromRelatedEnterpriseAndJointlyOperating': '45035770.67',
 'minorityInterestIncome': 91203287.92,
 'netProfit': 521516997.38,
 'netProfitAttributedToParentCompanyOwner': 430313709.46,
 'nonOperatingExpenditure': 13775609.35,
 'nonOperatingIncome': 27864700.17,
 'operatingCosts': 679308123.4,
 'operatingProfit': 619292362.12,
 'operatingRevenue': 1465863805.45,
 'operatingTotalCosts': 1388050398.5,
 'otherComprehensiveIncome': -50030885.08,
 'reportDate': '2017-06-30',
 'reportEventDate': '2017-08-29',
 'securityId': 'stock_sz_300027',
 'sellingExpenses': 261148997.92,
 'totalProfits': 633381452.94}

```

### 财务报表的勾稽关系验证 ###  
```python
# 营业利润=营业收入-营业成本-营业税金及附加-销售费用-管理费用-财务费用-资产减值损失+公允价值变动收益（损失的话用减）+投资收益
def check_operating_profit(security_item):
    income_statement_list = get_income_statement_items(security_item=security_item)
    for income_statement in income_statement_list:
        operatingProfit = income_statement["operatingRevenue"] \
                          - income_statement["operatingCosts"] \
                          - income_statement["businessTaxesAndSurcharges"] \
                          - income_statement["sellingExpenses"] \
                          - income_statement["ManagingCosts"] \
                          - income_statement["financingExpenses"] \
                          - income_statement["assetsDevaluation"] \
                          + income_statement["incomeFromChangesInFairValue"] \
                          + income_statement["investmentIncome"]
        diff = operatingProfit - income_statement["operatingProfit"]
        if abs(diff) >= 1:
            print("{} operating profit calculating not pass,calculating result:{},report result:{}".format(
                income_statement['id'], operatingProfit, income_statement["operatingProfit"]))
        else:
            print("{} operating profit calculating pass".format(income_statement['id']))
```
可以用该工具迅速检查财务报表的质量,同时也可以让你对财务报表有更深入的认识.[*更多例子*](./fooltrader/datamanager/finance_check.py)
```bash
In [3]: from fooltrader.datamanager import finance_check

In [4]: finance_check.check_operating_profit('300027')
stock_sz_300027_20061231 operating profit calculating pass
...
stock_sz_300027_20170630 operating profit calculating pass
stock_sz_300027_20170930 operating profit calculating pass
```
我的博客介绍[*fooltrader投资之财务指标*](https://foolcage.github.io/investing/fooltrader/2018/03/02/basic-finance-indicator.html)


### 事件(消息)数据 ###
```bash
In [12]: ft.get_finance_forecast_event('000002')
             timestamp reportPeriod       securityId type                                        description  preEPS  changeStart  change                          id
timestamp                                                                                                                                                            
2004-04-02  2004-04-02   2004-03-31  stock_sz_000002   预增                   预计公司2004年第1季度净利润较去年同期增长幅度超过150%。     NaN          NaN    1.50  stock_sz_000002_2004-04-02
2004-07-05  2004-07-05   2004-06-30  stock_sz_000002   预增                   预计公司2004年上半年度净利润较去年同期增长幅度将超过50%。     NaN          NaN    0.50  stock_sz_000002_2004-07-05
2005-01-12  2005-01-12   2004-12-31  stock_sz_000002   预增                     预计本公司2004年全年净利润较去年增长50%－65%之间。     NaN          NaN    0.65  stock_sz_000002_2005-01-12
2005-04-06  2005-04-06   2005-03-31  stock_sz_000002   预增                  预计本公司2005年1季度净利润较上年同期增长100%－150％。     NaN          NaN    1.50  stock_sz_000002_2005-04-06
2005-04-25  2005-04-25   2005-06-30  stock_sz_000002   预增                   预计本公司2005年上半年净利润较去年同期增长150—200%。     NaN          NaN    2.00  stock_sz_000002_2005-04-25
2005-08-01  2005-08-01   2005-09-30  stock_sz_000002   预增                预计2005年1～9月份可实现净利润将较去年同期增长110～130%。     NaN          NaN    1.30  stock_sz_000002_2005-08-01
2006-01-06  2006-01-06   2005-12-31  stock_sz_000002   预增                        预计本公司2005年全年净利润较去年增幅将超过50%。     NaN          NaN    0.50  stock_sz_000002_2006-01-06
2006-03-21  2006-03-21   2006-03-31  stock_sz_000002   预增               经初步测算，预计本公司2006年第1季度净利润较上年同期增长超过50%。     NaN          NaN    0.50  stock_sz_000002_2006-03-21
2006-06-23  2006-06-23   2006-06-30  stock_sz_000002   预增                     预计本公司2006年半年度净利润较上年同期增长50%~60%     NaN          NaN    0.60  stock_sz_000002_2006-06-23
2006-09-28  2006-09-28   2006-09-30  stock_sz_000002   预增                     预计2006年一至三季度净利润较上年同期增长50%-60%。     NaN          NaN    0.60  stock_sz_000002_2006-09-28
2007-01-12  2007-01-12   2006-12-31  stock_sz_000002   预增                          预计2006年全年净利润较去年增长50%-65%。    0.26          NaN    0.65  stock_sz_000002_2007-01-12
2007-04-04  2007-04-04   2007-03-31  stock_sz_000002   预增                    预计2007年第一季度净利润较上年同期增长幅度为50-60%。     NaN          NaN    0.60  stock_sz_000002_2007-04-04
2007-10-30  2007-10-30   2007-12-31  stock_sz_000002   预增                      公司预计2007年全年净利润较去年增长100%-150%。     NaN          NaN    1.50  stock_sz_000002_2007-10-30
2015-04-03  2015-04-03   2015-03-31  stock_sz_000002   预减  预计2015年1月1日-2015年3月31日归属于上市公司股东的净利润为盈利：60,000万...    0.14        -0.61   -0.54  stock_sz_000002_2015-04-03

In [13]: ft.get_finance_report_event('600338')
           reportPeriod       securityId   timestamp                  title                                                url                          id
timestamp                                                                                                                                                 
2010-02-12   2009-12-31  stock_sh_600338  2010-02-12  西藏珠峰工业股份有限公司2009年年度报告  http://vip.stock.finance.sina.com.cn/corp/view...  stock_sh_600338_2010-02-12
2011-04-27   2010-12-31  stock_sh_600338  2011-04-27                ST珠峰：年报  http://vip.stock.finance.sina.com.cn/corp/view...  stock_sh_600338_2011-04-27
2012-04-26   2011-12-31  stock_sh_600338  2012-04-26  西藏珠峰工业股份有限公司2011年年度报告  http://vip.stock.finance.sina.com.cn/corp/view...  stock_sh_600338_2012-04-26
2013-03-06   2012-12-31  stock_sh_600338  2013-03-06         西藏珠峰工业股份有限公司年报  http://vip.stock.finance.sina.com.cn/corp/view...  stock_sh_600338_2013-03-06
2014-04-30   2013-12-31  stock_sh_600338  2014-04-30  西藏珠峰工业股份有限公司2013年年度报告  http://vip.stock.finance.sina.com.cn/corp/view...  stock_sh_600338_2014-04-30
2015-04-30   2014-12-31  stock_sh_600338  2015-04-30         西藏珠峰工业股份有限公司年报  http://vip.stock.finance.sina.com.cn/corp/view...  stock_sh_600338_2015-04-30
2016-04-15   2015-12-31  stock_sh_600338  2016-04-15                 西藏珠峰年报  http://vip.stock.finance.sina.com.cn/corp/view...  stock_sh_600338_2016-04-15
2017-01-05   2015-12-31  stock_sh_600338  2017-01-05     西藏珠峰2015年年度报告（更正稿）  http://vip.stock.finance.sina.com.cn/corp/view...  stock_sh_600338_2017-01-05
2017-02-28   2016-12-31  stock_sh_600338  2017-02-28          西藏珠峰2016年年度报告  http://vip.stock.finance.sina.com.cn/corp/view...  stock_sh_600338_2017-02-28
2018-03-10   2017-12-31  stock_sh_600338  2018-03-10          西藏珠峰2017年年度报告  http://vip.stock.finance.sina.com.cn/corp/view...  stock_sh_600338_2018-03-10

```
### 各指数数据 ###
```
In [14]: ft.get_kdata('index_sh_000001')
             timestamp    code  name        low       open      close       high     volume      turnover       securityId   preClose    change  changePct  turnoverRate          tCap          mCap     pe
timestamp                                                                                                                                                                                                  
2018-06-11  2018-06-11  000001  上证指数  3037.9138  3057.3393  3052.7831  3063.6102  108563786  1.430373e+11  index_sh_000001  3067.1478  -14.3647    -0.4683        0.3412  3.199517e+13  2.689125e+13  15.06
2018-06-12  2018-06-12  000001  上证指数  3034.1012  3053.0279  3079.8018  3081.4473  113275096  1.544691e+11  index_sh_000001  3052.7831   27.0187     0.8851        0.3545  3.229036e+13  2.719762e+13  15.22
2018-06-13  2018-06-13  000001  上证指数  3044.1198  3071.4636  3049.7965  3071.4636  119607886  1.559353e+11  index_sh_000001  3079.8018  -30.0053    -0.9743        0.3733  3.205392e+13  2.699151e+13  15.09
2018-06-14  2018-06-14  000001  上证指数  3032.4062  3038.0704  3044.1597  3066.0469  115469487  1.475888e+11  index_sh_000001  3049.7965   -5.6368    -0.1848        0.3618  3.193968e+13  2.694981e+13  15.04
2018-06-15  2018-06-15  000001  上证指数  3008.7324  3037.4522  3021.9008  3048.7967  144532571  1.621960e+11  index_sh_000001  3044.1597  -22.2589    -0.7312        0.4490  3.171228e+13  2.680721e+13  14.93

```
### 技术指标 ###  
```bash
In [15]: ft.macd('000778',start_date='20170101',end_date='20170301')

            close  close_ema12  close_ema26      diff       dea      macd
timestamp                                                                
2017-01-03   5.21          NaN          NaN       NaN       NaN       NaN
2017-01-04   5.24          NaN          NaN       NaN       NaN       NaN
2017-01-05   5.31          NaN          NaN       NaN       NaN       NaN
2017-01-06   5.28          NaN          NaN       NaN       NaN       NaN
2017-01-09   5.33          NaN          NaN       NaN       NaN       NaN
2017-01-10   5.30          NaN          NaN       NaN       NaN       NaN
2017-01-11   5.34          NaN          NaN       NaN       NaN       NaN
2017-01-12   5.21          NaN          NaN       NaN       NaN       NaN
2017-01-13   5.11          NaN          NaN       NaN       NaN       NaN
2017-01-16   4.95          NaN          NaN       NaN       NaN       NaN
2017-01-17   5.00          NaN          NaN       NaN       NaN       NaN
2017-01-18   5.05     5.146697          NaN       NaN       NaN       NaN
2017-01-19   4.96     5.117975          NaN       NaN       NaN       NaN
2017-01-20   5.00     5.099825          NaN       NaN       NaN       NaN
2017-01-23   5.05     5.092159          NaN       NaN       NaN       NaN
2017-01-24   5.06     5.087212          NaN       NaN       NaN       NaN
2017-01-25   5.06     5.083025          NaN       NaN       NaN       NaN
2017-01-26   5.07     5.081022          NaN       NaN       NaN       NaN
2017-02-03   5.03     5.073172          NaN       NaN       NaN       NaN
2017-02-06   5.03     5.066530          NaN       NaN       NaN       NaN
2017-02-07   5.01     5.057833          NaN       NaN       NaN       NaN
2017-02-08   5.05     5.056628          NaN       NaN       NaN       NaN
2017-02-09   5.12     5.066378          NaN       NaN       NaN       NaN
2017-02-10   5.27     5.097704          NaN       NaN       NaN       NaN
2017-02-13   5.31     5.130365          NaN       NaN       NaN       NaN
2017-02-14   5.84     5.239540     5.184121  0.055419  0.055419  0.000000
2017-02-15   6.09     5.370380     5.251223  0.119157  0.068166  0.101981
2017-02-16   5.98     5.464167     5.305206  0.158961  0.086325  0.145271
2017-02-17   5.70     5.500449     5.334450  0.165999  0.102260  0.127478
2017-02-20   5.78     5.543457     5.367454  0.176003  0.117009  0.117989
2017-02-21   5.81     5.584464     5.400235  0.184229  0.130453  0.107552
2017-02-22   5.95     5.640700     5.440959  0.199742  0.144310  0.110862
2017-02-23   5.81     5.666746     5.468295  0.198451  0.155139  0.086625
2017-02-24   5.69     5.670324     5.484718  0.185606  0.161232  0.048748
2017-02-27   5.59     5.657966     5.492516  0.165450  0.162076  0.006749
2017-02-28   5.66     5.658279     5.504922  0.153357  0.160332 -0.013950
2017-03-01   5.63     5.653928     5.514187  0.139741  0.156214 -0.032945

```
>我们不需要那么多技术指标,但一定要知道所使用指标的内涵,所以,我们选择自己计算;没错,由于数据的统一性,理所当然地,计算的统一性也有了.
不管是A股,港股,还是数字货币,不管是1分钟级别,还是日线,使用的都是统一的api.


更多用法请查看[*api文档*](http://fooltrader.readthedocs.io/en/latest/api.html).  

## 1.3 **回测**  

策略的编写,可以采用事件驱动或者时间漫步的方式,查看[*设计文档*](./docs/trader.md)  
注意:回测框架目前还处于非常初期的阶段  
```python
class EventTrader(Trader):
    def on_init(self):
        self.trader_id = 'aa'
        self.only_event_mode = True
        self.universe = ['stock_sz_000338']
        self.df_map = {}

    def on_day_bar(self, bar_item):
        current_security = bar_item['securityId']
        current_df = self.df_map.get(current_security, pd.DataFrame())
        if current_df.empty:
            self.df_map[current_security] = current_df

        current_df = current_df.append(bar_item, ignore_index=True)
        self.df_map[current_security] = current_df

        if len(current_df.index) == 10:
            ma5 = np.mean(current_df.loc[5:, 'close'])
            ma10 = np.mean(current_df.loc[:, 'close'])
            # 5日线在10日线上,并且没有持仓,就买入
            if ma5 > ma10 and not self.account_service.get_position(current_security):
                self.buy(security_id=current_security, current_price=bar_item['close'])
            # 5日线在10日线下,并且有持仓,就卖出
            elif ma5 < ma10 and self.account_service.get_position(current_security):
                self.sell(security_id=current_security, current_price=bar_item['close'])
            current_df = current_df.loc[1:, ]
            self.df_map[current_security] = current_df
```

运行策略可以实时查看效果,并做进一步的评估
![](./screenshots/trader.gif)

# 2. 架构图
fooltrader是一个层次清晰的系统,你可以在不同的层次对其进行使用,也可以扩展,改造或替换里面的模块.  

![](./screenshots/architecture.png)

# 3. 使用step by step
使用的层次跟架构图里面的模块是一一对应的, 你可以在任何step停下来,进行扩展或者对接你自己熟悉的系统.  
当然,还是希望你全部跑通,因为这里的每个模块的技术选型都是经过精心考虑的,并且后续会不停完善.  

### 3.1 环境准备  
操作系统:Ubuntu 16.04.3 LTS  
原则上,其他也可以,系统使用的组件都是跨平台的,但我只在ubuntu和mac运行过    
内存:>=8G  
硬盘:越大越好  

clone或者fork代码  
```bash
$ git clone https://github.com/foolcage/fooltrader.git
```
```bash
$ cd fooltrader
$ ./init_env.sh
```
如果你最后看到:  
```bash
Requirements installed.  
env ok
```
那么恭喜你,你可以以各种姿势去玩耍了.

两种方式去下载历史数据(目前包含到2018-07-19的数据)
* 百度网盘[*data.zip*](https://pan.baidu.com/s/1-s9ZdzXTCyTJUxhRMAd5Kw).
>直接解压可用
* wget https://gitee.com/null_071_4607/fooltrader-data/raw/master/2018-07-19/dataa{a-j}
> 讲a-j个文件下载(目前速度最快的方式),然后合并:cat data* > data.zip 后再解压
* ~~git clone https://gitee.com/null_071_4607/fooltrader-data~~
>~~跟百度网盘是一样的数据，split过的，进入2018-07-19目录，cat data* > data.zip 后再解压~~

* 股票tick数据：https://pan.baidu.com/s/10LR1Cy6ZGZMQiaZ8Lh4_QA#list/path=%2F
> 这个数据太大，大概包含到2018年3月份的数据，split过的，
> cat 000* > 000.zip 后再解压

看一下[*数据协议*](./docs/contract.md),设置好FOOLTRADER_STORE_PATH,解压下载的文件到该目录.  
然后使用使用[*定时脚本*](./fooltrader/sched)每天抓取增量数据.  
```bash
$ source ve/bin/activate
抓股票列表
$ python fooltrader/sched/sched_stock_meta.py
抓行情
$ python fooltrader/sched/sched_china_stock_quote.py
抓财报
$ python fooltrader/sched/sched_finance.py
```
该项目的目的之一是方便大家共享数据,不需要每个人都去抓历史数据而导致被屏蔽.  
也可以用该[*脚本*](./fooltrader/datamanager/zipdata.py)对数据进行打包共享  

这些脚本会定时去抓取"缺少"的数据,在历史数据完整性检查通过后,其实就是只是抓取当天的数据,这样我们就有了一个自动化自我维护的完整数据源.  

这里把抓取数据作为一个单独的模块,而不是像某些开源项目那样api和爬虫耦合在一起,主要是为了:
> 爬虫只干爬虫的事:专注抓取的速度,更好的数据分类,数据补全,防屏蔽等  
> api设计只依赖[*数据协议*](./docs/contract.md),从而具有更好的速度和灵活性

最后强调一下,数据抓下来了,怎么使用?请参考[*数据协议*](./docs/contract.md)  
到这里,如果你不想使用elastic-search,也不想使用python,你就是想用java,mysql,或者你superset,redash,hadoop啥的玩得很熟,没问题,根据数据协议你应该很容易的把数据放到你需要的地方进行研究.
当然,我更希望你把代码贡献到connector里面,pr给我,既提高自己的代码水平,又方便了需要使用的人,岂不快哉?  
### 3.4 elastic-search和kibana安装(6.1.1)  
>仅仅只是把数据换一个存储,系统就发生了不可思议的变化.

可以参考官方文档进行安装:https://www.elastic.co/guide/en/elastic-stack/current/installing-elastic-stack.html  
也可以用以下命令来完成:  
```bash
$ #下载xpack
$ wget https://artifacts.elastic.co/downloads/packs/x-pack/x-pack-6.1.1.zip
$ #下载es
$ wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-6.1.1.zip
$ unzip elasticsearch-6.1.1.zip
$ cd elasticsearch-6.1.1/
$ #为es安装xpcck插件,就是刚刚下载的那个x-pack-6.1.1.zip,格式为file://+其路径
$ bin/elasticsearch-plugin install file:///path/to/file/x-pack-6.1.1.zip
$ #用fooltrader中的elasticsearch.yml覆盖es默认配置
$ cp ../fooltrader/config/elasticsearch.yml config/
$ #启动es,可根据自己的情况更改heap大小,<=32g
$ ES_JAVA_OPTS="-Xms8g -Xmx8g"  ./bin/elasticsearch
$
$ #下载kibana
$ wget https://artifacts.elastic.co/downloads/kibana/kibana-6.1.1-linux-x86_64.tar.gz
$ tar -xzf kibana-6.1.1-linux-x86_64.tar.gz
$ cd kibana-6.1.1-linux-x86_64/
$ #为kibana安装xpcck插件,就是刚刚下载的那个x-pack-6.1.1.zip,格式为file://+其路径
$ bin/kibana-plugin install file:///path/to/file/x-pack-6.1.1.zip
$ #用fooltrader中的kibana.yml覆盖kibana默认配置
$ cp ../fooltrader/config/kibana.yml config/
$ ./bin/kibana
```

### 3.5 数据存储到elastic-search  
到这里,我还是默认你在fooltrader的ipython环境下.
```bash
In [1]: from fooltrader.connector import es_connector
#股票元信息->es
In [2]: es_connector.security_meta_to_es()
#指数数据->es
In [3]: es_connector.kdata_to_es(security_type='index')
#个股k线->es
In [4]: es_connector.kdata_to_es(security_type='stock')
#你也可以多开几个窗口,指定范围,提高索引速度
In [4]: es_connector.kdata_to_es(start='002000',end='002999')
#财务数据->es
In [5]: es_connector.finance_sheet_to_es('balance_sheet')
In [5]: es_connector.finance_sheet_to_es('cash_flow_statement')
In [5]: es_connector.finance_sheet_to_es('income_statement')
```
更多功能可以直接查看es_connector的源码,也可以加到定时任务里面,所有索引函数都做了时间判断,只会添加没有添加的数据.

然后,我们简单的来领略一下它的威力  
查询2017年中报净利润top 5
```bash
curl -XPOST 'localhost:9200/income_statement/doc/_search?pretty&filter_path=hits.hits._source' -H 'Content-Type: application/json' -d'
{
  "query": {
    "range": {
      "reportDate": {
        "gte": "20170630",
        "lte": "20170630"
      }
    }
  },
  "size": 5,
  "sort": [
    {
      "netProfit": {
        "order": "desc"
      }
    }
  ]
}
'
{
  "hits": {
    "hits": [
      {
        "_source": {
          "exchangeGains": 1.3242E10,
          "netProfit": 1.827E9,
          "securityId": "stock_sh_601318",
          "investmentIncome": 2.0523E10,
          "operatingProfit": 7.8107E10,
          "accumulatedOtherComprehensiveIncome": 2.0E8,
          "attributableToMinorityShareholders": 6.5548E10,
          "sellingExpenses": 1.0777E10,
          "investmentIncomeFromRelatedEnterpriseAndJointlyOperating": "398259000000.00",
          "id": "stock_sh_601318_20170630",
          "minorityInterestIncome": 6.238E10,
          "code": "601318",
          "otherComprehensiveIncome": 6.5506E10,
          "nonOperatingIncome": 4.006E9,
          "financingExpenses": 0.0,
          "reportEventDate": "2017-08-18",
          "netProfitAttributedToParentCompanyOwner": 5.778E10,
          "disposalLossOnNonCurrentLiability": 9.01E8,
          "incomeFromChangesInFairValue": -2.56E8,
          "incomeTaxExpense": 2.2E7,
          "operatingTotalCosts": 3.4139E11,
          "assetsDevaluation": 8.75E8,
          "EPS": 1.9449E10,
          "operatingCosts": 9.4E7,
          "attributableToOwnersOfParentCompany": 1.58E8,
          "ManagingCosts": 6.402E10,
          "totalProfits": 8.403E9,
          "dilutedEPS": 2.4575E10,
          "reportDate": "20170630",
          "businessTaxesAndSurcharges": 9.442E9,
          "operatingRevenue": 4.63765E11,
          "nonOperatingExpenditure": 1.35892E11
        }
      ]
    }
  }
}
```
实际上REST接口天然就有了,做跨平台接口非常方便,根据[*数据协议*](./docs/contract.md) 和ES DSL可以非常方便的进行查询和聚合计算.

### 3.6 使用kibana进行分析
(文档待完善)

### 3.7 回测
(文档待完善)

### 3.8 交易
(文档待完善)

# 支持的功能
* 爬虫代理框架  

>可配置代理服务器池和并发数,从而提高爬虫的健壮性

* 数据抓取  
  * A股标的信息抓取  
  * A股tick数据抓取  
  * A股日线数据抓取  
  * A股财务数据抓取  
  * A股事件抓取
  * 数字货币行情
  * 期货数据  

>数据的处理方式是,先定义[*数据协议*](./docs/contract.md),再寻找数据源,这样做的好处是:数据协议的稳定为整个系统的稳定打下坚实的基础,多数据源比较提高数据准确性,多数据源聚合提高数据完整性.

* 常用技术指标计算(ma,ema,macd等)

* 回测框架

>小金属涨疯了,但相关的上市公司股价还在历史新低,我是不是可以买一点?  
金叉买,死叉卖,在不同级别上表现如何?在不同标的上表现如何?  
相同的策略,如何快速的在所有标的上回测,并进行对比?  
利润增长,股价也增长?或者提前反映?滞后反映?各种表现的比例如何?  
各个策略之间如何通信,从而形成合力?  
#### 没错:回测框架必须要考虑这些问题  

# TODO
* 交易DSL设计
* WEB管理界面,向导式生成策略
* 实时行情及kafka实时计算
* 集成vnpy的交易接口
* 港股数据抓取

# 联系方式  
QQ群:300911873  
如果你喜欢该项目,请加星支持一下,并在申请入群时告知github user name.  
