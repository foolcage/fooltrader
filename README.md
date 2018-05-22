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

### 获取利润表 ###
```bash
In [1]: from fooltrader.api import finance
In [2]: finance.get_income_statement_items('300027',report_period='2017-06-30')
#试一试
#finance.get_balance_sheet_items('300027',,report_event_date='2017-01-01')
#finance.get_cash_flow_statement_items('300027')
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

### 行情信息 ###
K线数据
```bash
In [5]: from fooltrader.api import quote

In [6]: quote.get_kdata('300027',start_date='20170630',end_date='20170715')
#试一试
#quote.get_kdata('300027',start_date='20170630',end_date='20170715',fuquan='qfq')
#quote.get_kdata('300027',start_date='20170630',end_date='20170715',fuquan='hfq')
Out[6]:
             timestamp    code  name   low  open  close  high    volume      turnover       securityId  preClose  change  changePct  turnoverRate          tCap          mCap  factor
timestamp                                                                                                                                                                            
2017-06-30  2017-06-30  300027  华谊兄弟  8.03  8.11   8.09  8.11   9515735  7.684533e+07  stock_sz_300027      8.11   -0.02    -0.2466        0.3832  2.244575e+10  2.008766e+10  15.055
2017-07-03  2017-07-03  300027  华谊兄弟  8.07  8.09   8.20  8.22  15577742  1.270549e+08  stock_sz_300027      8.09    0.11     1.3597        0.6274  2.275095e+10  2.036079e+10  15.055
2017-07-04  2017-07-04  300027  华谊兄弟  8.12  8.20   8.15  8.22   8672705  7.068477e+07  stock_sz_300027      8.20   -0.05    -0.6098        0.3493  2.261222e+10  2.023664e+10  15.055
2017-07-05  2017-07-05  300027  华谊兄弟  8.11  8.15   8.19  8.22  12458305  1.017991e+08  stock_sz_300027      8.15    0.04     0.4908        0.5017  2.272320e+10  2.033596e+10  15.055
2017-07-06  2017-07-06  300027  华谊兄弟  8.17  8.20   8.20  8.29  18642574  1.533405e+08  stock_sz_300027      8.19    0.01     0.1221        0.7508  2.275095e+10  2.036079e+10  15.055
2017-07-07  2017-07-07  300027  华谊兄弟  8.13  8.18   8.17  8.19   9414275  7.679682e+07  stock_sz_300027      8.20   -0.03    -0.3659        0.3791  2.266771e+10  2.028630e+10  15.055
2017-07-10  2017-07-10  300027  华谊兄弟  8.08  8.18   8.09  8.19  12679949  1.029643e+08  stock_sz_300027      8.17   -0.08    -0.9792        0.5107  2.244575e+10  2.008766e+10  15.055
2017-07-11  2017-07-11  300027  华谊兄弟  8.06  8.10   8.08  8.13  11412820  9.235337e+07  stock_sz_300027      8.09   -0.01    -0.1236        0.4596  2.241801e+10  2.006283e+10  15.055
2017-07-12  2017-07-12  300027  华谊兄弟  7.93  8.07   8.03  8.10  13776145  1.104951e+08  stock_sz_300027      8.08   -0.05    -0.6188        0.5548  2.227928e+10  1.993868e+10  15.055
2017-07-13  2017-07-13  300027  华谊兄弟  8.09  8.10   8.28  8.37  43554957  3.590739e+08  stock_sz_300027      8.03    0.25     3.1133        1.7541  2.297291e+10  2.055944e+10  15.055
2017-07-14  2017-07-14  300027  华谊兄弟  8.23  8.25   8.41  8.55  37967053  3.193673e+08  stock_sz_300027      8.28    0.13     1.5700        1.5291  2.333359e+10  2.088223e+10  15.055
```
tick数据
```bash
In [7]: for tick in quote.get_ticks('300027',the_date='2017-07-03'):
    ...:     print(tick)
    ...:     
    ...:     
#试一试
#quote.get_ticks('300027',start='2017-06-30',end='2017-07-10')
                               timestamp  price  volume  turnover  direction    code       securityId
timestamp                                                                                            
2017-07-03 09:25:03  2017-07-03 09:25:03   8.09      41     33169          1  300027  stock_sz_300027
2017-07-03 09:30:03  2017-07-03 09:30:03   8.09      10      8090          1  300027  stock_sz_300027
...                                  ...    ...     ...       ...        ...     ...              ...
2017-07-03 14:57:00  2017-07-03 14:57:00   8.19       4      3276         -1  300027  stock_sz_300027
2017-07-03 14:57:03  2017-07-03 14:57:03   8.19       0         0         -1  300027  stock_sz_300027
2017-07-03 15:00:03  2017-07-03 15:00:03   8.20    4394   3603079          1  300027  stock_sz_300027

[2313 rows x 7 columns]

```

### 事件(消息)数据 ###
```bash
In [8]: from fooltrader.api import event

In [9]: for item in event.get_forecast_items('000338'):
   ...:     print(item)
   ...:     
{'changeStart': None, 'reportDate': '2008-01-28', 'id': 'stock_sz_000338_2008-01-28', 'preEPS': None, 'securityId': 'stock_sz_000338', 'reportPeriod': '2007-12-31', 'description': '潍柴动力预计2007年1-12月净利润较2006年度备考合并净利润增长约140%左右。', 'change': 1.4, 'type': '预增'}
{'changeStart': None, 'reportDate': '2008-07-24', 'id': 'stock_sz_000338_2008-07-24', 'preEPS': 1.87, 'securityId': 'stock_sz_000338', 'reportPeriod': '2008-06-30', 'description': '预计本公司2008年1-6月归属于母公司所有者净利润与2007年同期调整前及调整后的归属于母公司所有者净利润相比增长50%-100%之间。', 'change': 1.0, 'type': '预增'}
{'changeStart': None, 'reportDate': '2009-08-19', 'id': 'stock_sz_000338_2009-08-19', 'preEPS': 3.19, 'securityId': 'stock_sz_000338', 'reportPeriod': '2009-06-30', 'description': '预计本公司2009年半年度营业收入约为人民币158亿元，营业利润约在人民币15-18亿元之间，利润总额约在人民币15-18亿元之间，归属于上市公司股东的净利润约在人民币10.0-12.5亿元之间。', 'change': 0.0, 'type': '预降'}
...
{'changeStart': 1.4, 'reportDate': '2017-04-14', 'id': 'stock_sz_000338_2017-04-14', 'preEPS': 0.11, 'securityId': 'stock_sz_000338', 'reportPeriod': '2017-03-31', 'description': '预计2017年1-3月归属于上市公司股东的净利润为：109,600.00万元至123,300.00万元，较上年同期相比变动幅度：140.00%至170.00%。', 'change': 1.7, 'type': '预增'}
{'changeStart': 0.7, 'reportDate': '2017-04-28', 'id': 'stock_sz_000338_2017-04-28', 'preEPS': 0.26, 'securityId': 'stock_sz_000338', 'reportPeriod': '2017-06-30', 'description': '预计2017年1-6月归属于上市公司股东的净利润为：183,000.00万元至215,000.00万元，较上年同期相比变动幅度：70.00%至100.00%。', 'change': 1.0, 'type': '预增'}
{'changeStart': 1.5, 'reportDate': '2017-08-31', 'id': 'stock_sz_000338_2017-08-31', 'preEPS': 0.38, 'securityId': 'stock_sz_000338', 'reportPeriod': '2017-09-30', 'description': '预计2017年1-9月归属于上市公司股东的净利润为：385,000.00万元至431,400.00万元，较上年同期相比变动幅度：150.00%至180.00%。', 'change': 1.8, 'type': '预增'}
```

### 技术指标 ###  
```bash
In [10]: from fooltrader.api import technical
In [11]: technical.macd('000778',start_date='20170101',end_date='20170301')
Out[11]:
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

如果你想直接使用,只需要:
```bash
#在python3.5环境下,或者使用virtualenv
pip install fooltrader
```
下载打包好的历史数据[*data.zip*](https://pan.baidu.com/s/1dmZaPo).  
看一下[*数据协议*](./docs/contract.md),设置好FOOLTRADER_STORE_PATH,解压下载的文件到该目录.  
然后使用[*定时脚本1*](./fooltrader/sched/sched_finance.py)和[*定时脚本2*](./fooltrader/sched/sched_quote.py)每天抓取增量数据.  
该项目的目的之一是方便大家共享数据,不需要每个人都去抓历史数据而导致被屏蔽.  
也可以用该[*脚本*](./fooltrader/datamanager/zipdata.py)对数据进行打包共享  

*不过由于该项目还在快速更新中,最好还是按下面的步骤直接用源码来搞*  
### 3.2 初始化python环境
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
### 3.3 抓取数据
```bash
$ source ve/bin/activate
$ ./ve/bin/ipython
In [1]: from fooltrader.datamanager import datamanager
#抓取股票元数据
In [2]: datamanager.crawl_stock_meta()
#抓取指数数据
In [3]: datamanager.crawl_index_quote()
#抓取个股K线和tick数据
In [4]: datamanager.crawl_stock_quote(start_code='002797',end_code='002798',crawl_tick=False)
#抓取财务数据
In [5]: datamanager.crawl_finance_data(start_code='002797',end_code='002798')
```
这里把抓取数据作为一个单独的模块,而不是像某些开源项目那样api和爬虫耦合在一起,主要是为了:
> 爬虫只干爬虫的事:专注抓取的速度,更好的数据分类,数据补全,防屏蔽等  
> api设计只依赖[*数据协议*](./docs/contract.md),从而具有更好的速度和灵活性


抓取每天的增量数据只需要:
```bash
$ ./sched_finance.sh
```
```bash
$ ./sched_quote.sh
```
该脚本会定时去抓取"缺少"的数据,在历史数据完整性检查通过后,其实就是只是抓取当天的数据,这样我们就有了一个自动化自我维护的完整数据源.  
可在sched_quote.py文件中进行对定时任务进行配置:  
```python
#每天17:00运行
@sched.scheduled_job('cron', hour=17, minute=00)
def scheduled_job1():
    crawl_stock_quote('000001', '002999')
    crawl_index_quote()


@sched.scheduled_job('cron', hour=17, minute=20)
def scheduled_job2():
    crawl_stock_quote('300000', '300999')


@sched.scheduled_job('cron', hour=17, minute=40)
def scheduled_job3():
    crawl_stock_quote('600000', '666666')
```

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
In [2]: es_connector.stock_meta_to_es()
#指数数据->es
In [3]: es_connector.index_kdata_to_es()
#个股k线->es
In [4]: es_connector.stock_kdata_to_es()
#你也可以多开几个窗口,指定范围,提高索引速度
In [4]: es_connector.stock_kdata_to_es(start='002000',end='002999')
#财务数据->es
In [5]: es_connector.balance_sheet_to_es()
In [5]: es_connector.income_statement_to_es()
In [5]: es_connector.cash_flow_statement_to_es()
```

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
* 期货数据抓取
* 港股数据抓取

# 联系方式  
QQ群:300911873  
如果你喜欢该项目,请加星支持一下,并在申请入群时告知github user name.  
