该文档定义了fooltrader的数据协议,包括数据字段的含义,文件的存储目录结构,文件的格式,elastic search的mapping,kafka的schema.
# 基础概念
* 证券类型(type)  
stock,future,bond等
* 交易所(exchange)  
sz,sh等
* 代码(code)  
000338,600388等
* 唯一标识标(security_id)  
结构为type_exchange_code,比如stock_sz_000338,代表A股中的潍柴动力.

# 目录结构
* 存储根目录  
settings.py里面  
```
#fooltrader的数据根目录
FILES_STORE = '/home/xuanqi/workspace/github/fooltrader/data'
```
* 具体结构
```
├── index(指数的数据)
│   ├── sh
│   │   └── 000001(上证指数)
│   │       └── kdata(k线数据)
│   │           └── 163_dayk.csv
│   └── sz
│       └── 399001(深证成指)
│           └── kdata
│               └── 163_dayk.csv
├── proxy
│   ├── http_proxy.csv
│   └── socks_proxy.csv
└── stock(股票的数据)
    ├── sh(上海交易所)
    │   └── 600000(股票代号)
    │       ├── event
    │       ├── finance
    │       ├── kdata
    │       │   ├── bfq
    │       │   │   └── dayk.csv
    │       │   └── hfq
    │       │       └── dayk.csv
    │       └── tick
    ├── sh.csv(上海交易所股票元数据)
    ├── sz(深圳交易所)
    │   └── 000002(股票代号)
    │       ├── event(事件数据)
    │       │   ├── finance_report.csv(财报公告事件)
    │       │   └── forecast.json(业绩预告事件)
    │       ├── finance(财务数据)
    │       │   ├── balance_sheet.xls(资产负债表)
    │       │   ├── cash_flow_statement.xls(现金流量表)
    │       │   └── income_statement.xls(利润表)
    │       ├── kdata(k线数据)
    │       │   ├── bfq(不复权的数据)
    │       │   │   ├── 163_dayk.csv(从163抓取的数据,这个数据现在合并过,质量最好)
    │       │   │   └── dayk.csv(新浪的数据)
    │       │   └── hfq(后复权的数据)
    │       │       └── dayk.csv(新浪的数据)
    │       └── tick(tick数据)
    │           ├── 2013-01-21.csv(某日的tick数据)
    │           └── 2013-01-22.csv
    └── sz.csv(深圳交易所股票元数据)
```
# csv文件字段
* 股票元数据
```
代码,名字,上市日期,所在交易所,类型,唯一标识,新浪行业,新浪区域
code,name,listDate,exchange,type,id,sinaIndustry,sinaArea
000001,平安银行,1991-04-03,sz,stock,stock_sz_000001,金融行业,"['深圳', '广东']"
000002,万  科Ａ,1991-01-29,sz,stock,stock_sz_000002,房地产,广东
000004,国农科技,1990-12-01,sz,stock,stock_sz_000004,生物制药,"['深圳', '广东']"
```

* 指数K线数据
```
日期,代码,名称,最低,开盘,收盘,最高,成交量(股),成交额(元),唯一标识,前收盘,涨跌额,涨跌幅(%),换手率(%),总市值,流通市值
timestamp,code,name,low,open,close,high,volume,turnover,securityId,preClose,change,changePct,turnoverRate,tCap,mCap,pe
2018-01-02,000001,上证指数,3314.0307,3314.0307,3348.3259,3349.053,202278860,227788461113.0,index_sh_000001,3307.1721,41.1538,1.2444,0.5595,34340879249962.87,29261135995966.35,18.91
2018-01-03,000001,上证指数,3345.2887,3347.7428,3369.1084,3379.9152,213836149,258366523235.0,index_sh_000001,3348.3259,20.7825,0.6207,0.5595,34340879249962.87,29261135995966.35,18.91
2018-01-04,000001,上证指数,3365.2954,3371.0,3385.7102,3392.8264,206955288,243090768694.0,index_sh_000001,3369.1084,16.6018,0.4928,0.5595,34340879249962.87,29261135995966.35,18.91
```
* 个股K线数据
```
日期,代码,名称,最低,开盘,收盘,最高,成交量(股),成交额(元),唯一标识,前收盘,涨跌额,涨跌幅(%),换手率(%),总市值,流通市值,复权因子
timestamp,code,low,open,close,high,volume,turnover,securityId,preClose,change,changePct,turnoverRate,tCap,mCap,factor
2017-12-19,000002,28.4,28.66,29.16,29.25,34008410,981540648.24,stock_sz_000002,28.46,0.7,2.4596,0.3497,321901672349.0,283557570902.0,127.564
2017-12-20,000002,28.52,29.09,28.6,29.1,32902669,943187281.92,stock_sz_000002,29.16,-0.56,-1.9204,0.3384,315719747229.0,278112020844.0,127.564
2017-12-21,000002,28.63,28.72,29.72,30.19,59516386,1756898867.87,stock_sz_000002,28.6,1.12,3.9161,0.612,328083597470.0,289003120961.0,127.564
```
价格为不复权数据,利用复权因子,可以非常方便的得出前复权和后复权数据,算法为:  
后复权价格=价格*复权因子  
前复权价格=价格/最新的复权因子  
可以看出,后复权价格是不变的,而前复权却依赖时间  

* tick数据  
```
时间,价格,成交额,成交量,方向(买:1,卖:-1,中性:0)
timestamp,price,volume,turnover,direction
09:47:50,11.74,544,638656,-1
09:47:47,11.74,5483,6437088,0
09:47:44,11.75,572,672852,1
```

* 财务数据
原始的xls文件有中文字段含义,不再赘述,熟悉财务的人也可以直接用excel来分析.
fooltrader里面的字段含义如下:
```
#资产负债表
class BalanceSheet(BaseDocType):
    id = Keyword()
    securityId = Keyword()
    code = Keyword()
    reportDate = Date()
    reportEventDate = Date()
    # 货币资金
    moneyFunds = Float()
    # 交易性金融资产
    heldForTradingFinancialAssets = Float()
    # 衍生金融资产
    derivative = Float()
    # 应收票据
    billsReceivable = Float()
    # 应收账款
    accountsReceivable = Float()
    # 预付款项
    prepaidAccounts = Float()
    # 应收利息
    interestReceivable = Float()
    # 应收股利
    dividendReceivable = Float()
    # 其他应收款
    otherReceivables = Float()

    # 买入返售金融资产
    buyingBackTheSaleOfFinancialAssets = Float()
    # 存货
    inventory = Float()
    # 划分为持有待售的资产
    assetsForSale = Float()
    # 一年内到期的非流动资产
    nonCurrentAssetsDueWithinOneYear = Float()

    # 待摊费用
    unamortizedExpenditures = Float()
    # 待处理流动资产损益
    waitDealIntangibleAssetsLossOrIncome = Float()

    # 其他流动资产
    otherCurrentAssets = Float()
    # 流动资产合计
    totalCurrentAssets = Float()

    # 非流动资产

    # 发放贷款及垫款
    loansAndPaymentsOnBehalf = Float()

    # 可供出售金融资产
    availableForSaleFinancialAssets = Float()
    # 持有至到期投资
    heldToMaturityInvestment = Float()
    # 长期应收款
    longTermReceivables = Float()
    # 长期股权投资
    longTermEquityInvestment = Float()
    # 投资性房地产
    investmentRealEstate = Float()
    # 固定资产净额
    NetfixedAssets = Float()
    # 在建工程
    constructionInProcess = Float()
    # 工程物资
    engineerMaterial = Float()
    # 固定资产清理
    fixedAssetsInLiquidation = Float()
    # 生产性生物资产
    productiveBiologicalAssets = Float()
    # 公益性生物资产
    nonProfitLivingAssets = Float()
    # 油气资产
    oilAndGasAssets = Float()
    # 无形资产
    intangibleAssets = Float()
    # 开发支出
    developmentExpenditure = Float()
    # 商誉
    goodwill = Float()
    # 长期待摊费用
    longTermDeferredExpenses = Float()
    # 递延所得税资产
    deferredIncomeTaxAssets = Float()
    # 其他非流动资产
    OtherNonCurrentAssets = Float()
    # 非流动资产合计
    nonCurrentAssets = Float()
    # 资产总计
    totalAssets = Float()

    # / *流动负债 * /
    # 短期借款
    shortTermBorrowing = Float()
    # 交易性金融负债
    transactionFinancialLiabilities = Float()
    # 应付票据
    billsPayable = Float()
    # 应付账款
    accountsPayable = Float()
    # 预收款项
    accountsReceivedInAdvance = Float()
    # 应付手续费及佣金
    handlingChargesAndCommissionsPayable = Float()
    # 应付职工薪酬
    employeeBenefitsPayable = Float()
    # 应交税费
    taxesAndSurchargesPayable = Float()
    # 应付利息
    interestPayable = Float()
    # 应付股利
    dividendpayable = Float()
    # 其他应付款
    otherPayables = Float()
    # 预提费用
    withholdingExpenses = Float()
    # 一年内的递延收益
    deferredIncomeWithinOneYear = Float()
    # 应付短期债券
    shortTermDebenturesPayable = Float()
    # 一年内到期的非流动负债
    nonCurrentLiabilitiesMaturingWithinOneYear = Float()
    # 其他流动负债
    otherCurrentLiability = Float()
    # 流动负债合计
    totalCurrentLiabilities = Float()

    # / *非流动负债 * /
    # 长期借款
    LongTermBorrowing = Float()
    # 应付债券
    bondPayable = Float()
    # 长期应付款
    longTermPayables = Float()
    # 长期应付职工薪酬
    longTermEmployeeBenefitsPayable = Float()
    # 专项应付款
    specialPayable = Float()
    # 预计非流动负债
    expectedNonCurrentLiabilities = Float()
    # 递延所得税负债
    deferredIncomeTaxLiabilities = Float()
    # 长期递延收益
    longTermDeferredRevenue = Float()
    # 其他非流动负债
    otherNonCurrentLiabilities = Float()
    # 非流动负债合计
    totalNonCurrentLiabilities = Float()
    # 负债合计
    totalLiabilities = Float()

    # / *所有者权益 * /
    # 实收资本(或股本)
    totalShareCapital = Float()

    # 资本公积
    capitalSurplus = Float()
    # 减：库存股
    treasuryStock = Float()
    # 其他综合收益
    otherComprehensiveIncome = Float()
    # 专项储备
    theSpecialReserve = Float()

    # 盈余公积
    surplusReserves = Float()
    # 一般风险准备
    generalRiskPreparation = Float()
    # 未分配利润
    undistributedProfits = Float()
    # 归属于母公司股东权益合计(净资产)
    bookValue = Float()

    # 少数股东权益
    minorityBookValue = Float()

    # 所有者权益(或股东权益)合计
    totalBookValue = Float()

    # 负债和所有者权益(或股东权益)总计
    totalLiabilitiesAndOwnersEquity = Float()

    class Meta:
        index = 'balance_sheet'
        doc_type = 'doc'
        all = MetaField(enabled=False)


#利润表
class IncomeStatement(BaseDocType):
    id = Keyword()
    securityId = Keyword()
    code = Keyword()
    reportDate = Date()
    reportEventDate = Date()
    # /*营业总收入*/
    # 营业收入
    operatingRevenue = Float()
    # /*营业总成本*/
    OperatingTotalCosts = Float()
    # 营业成本
    OperatingCosts = Float()
    # 营业税金及附加
    businessTaxesAndSurcharges = Float()
    # 销售费用
    sellingExpenses = Float()
    # 管理费用
    ManagingCosts = Float()
    # 财务费用
    financingExpenses = Float()
    # 资产减值损失
    assetsDevaluation = Float()
    # 公允价值变动收益
    incomeFromChangesInFairValue = Float()
    # 投资收益
    investmentIncome = Float()
    # 其中:对联营企业和合营企业的投资收益
    investmentIncomeFromRelatedEnterpriseAndJointlyOperating = Float()
    # 汇兑收益
    exchangeGains = Float()
    # /*营业利润*/
    operatingProfit = Float()
    # 加:营业外收入
    nonOperatingIncome = Float()
    # 减：营业外支出
    nonOperatingExpenditure = Float()
    # 其中：非流动资产处置损失
    disposalLossOnNonCurrentLiability = Float()
    # /*利润总额*/
    totalProfits = Float()
    # 减：所得税费用
    incomeTaxExpense = Float()
    # /*净利润*/
    netProfit = Float()
    # 归属于母公司所有者的净利润
    netProfitAttributedToParentCompanyOwner = Float()
    # 少数股东损益
    minorityInterestIncome = Float()
    # /*每股收益*/
    # 基本每股收益(元/股)
    EPS = Float()
    # 稀释每股收益(元/股)
    dilutedEPS = Float()
    # /*其他综合收益*/
    otherComprehensiveIncome = Float()
    # /*综合收益总额*/
    accumulatedOtherComprehensiveIncome = Float()
    # 归属于母公司所有者的综合收益总额
    attributableToOwnersOfParentCompany = Float()
    # 归属于少数股东的综合收益总额
    attributableToMinorityShareholders = Float()

    class Meta:
        index = 'income_statement'
        doc_type = 'doc'
        all = MetaField(enabled=False)

#现金流量表
class CashFlowStatement(DocType):
    id = Keyword()
    securityId = Keyword()
    code = Keyword()
    reportDate = Date()
    reportEventDate = Date()

    # /*一、经营活动产生的现金流量*/
    # 销售商品、提供劳务收到的现金
    cashFromSellingCommoditiesOrOfferingLabor = Float()
    # 收到的税费返还
    refundOfTaxAndFeeReceived = Float()
    # 收到的其他与经营活动有关的现金
    cashReceivedRelatingToOtherOperatingActivities = Float()
    # 经营活动现金流入小计
    subTotalOfCashInflowsFromOperatingActivities = Float()
    # 购买商品、接受劳务支付的现金
    cashPaidForGoodsAndServices = Float()
    # 支付给职工以及为职工支付的现金
    cashPaidToAndOnBehalfOfemployees = Float()
    # 支付的各项税费
    paymentsOfTaxesAndSurcharges = Float()
    # 支付的其他与经营活动有关的现金
    cashPaidRelatingToOtherOperatingActivities = Float()
    # 经营活动现金流出小计
    subTotalOfCashOutflowsFromOperatingActivities = Float()
    # 经营活动产生的现金流量净额
    netCashFlowsFromOperatingActivities = Float()
    # /*二、投资活动产生的现金流量*/
    # 收回投资所收到的现金
    cashReceivedFromDisposalOfInvestments = Float()
    # 取得投资收益所收到的现金
    cashReceivedFromReturnsOnIvestments = Float()
    # 处置固定资产、无形资产和其他长期资产所收回的现金净额
    netCashReceivedFromDisposalAssets = Float()
    # 处置子公司及其他营业单位收到的现金净额
    netCashReceivedFromDisposalSubsidiaries = Float()
    # 收到的其他与投资活动有关的现金
    cashReceivedFromOtherInvesting = Float()
    # 投资活动现金流入小计
    subTotalOfCashInflowsFromInvesting = Float()
    # 购建固定资产、无形资产和其他长期资产所支付的现金
    cashPaidToAcquireFixedAssets = Float()
    # 投资所支付的现金
    cashPaidToAcquireInvestments = Float()
    # 取得子公司及其他营业单位支付的现金净额
    netCashPaidToAcquireSubsidiaries = Float()
    # 支付的其他与投资活动有关的现金
    cashPaidRelatingToOtherInvesting = Float()
    # 投资活动现金流出小计
    subTotalOfCashOutflowsFromInvesting = Float()
    # 投资活动产生的现金流量净额
    netCashFlowsFromInvesting = Float()
    # /*三、筹资活动产生的现金流量*/
    # 吸收投资收到的现金
    cashReceivedFromCapitalContributions = Float()
    # 其中：子公司吸收少数股东投资收到的现金
    cashReceivedFromMinorityShareholdersOfSubsidiaries = Float()
    # 取得借款收到的现金
    cashReceivedFromBorrowings = Float()
    # 发行债券收到的现金
    cashReceivedFromIssuingBonds = Float()
    # 收到其他与筹资活动有关的现金
    cashReceivedRelatingToOtherFinancingActivities = Float()
    # 筹资活动现金流入小计
    subTotalOfCashInflowsFromFinancingActivities = Float()
    # 偿还债务支付的现金
    cashRepaymentsOfBorrowings = Float()
    # 分配股利、利润或偿付利息所支付的现金
    cashPaymentsForInterestExpensesAndDistributionOfDividendsOrProfits = Float()
    # 其中：子公司支付给少数股东的股利、利润
    cashPaymentsForDividendsOrProfitToMinorityShareholders = Float()
    # 支付其他与筹资活动有关的现金
    cashPaymentsRelatingToOtherFinancingActivities = Float()
    # 筹资活动现金流出小计
    subTotalOfCashOutflowsFromFinancingActivities = Float()
    # 筹资活动产生的现金流量净额
    netCashFlowsFromFinancingActivities = Float()
    # /*四、汇率变动对现金及现金等价物的影响*/
    effectOfForeignExchangeRate = Float()
    # /*五、现金及现金等价物净增加额*/
    netIncreaseInCash = Float()
    # 加:期初现金及现金等价物余额
    cashAtBeginningOfyear = Float()
    # /*六、期末现金及现金等价物余额*/
    cashAtEndOfyear = Float()
    # /*附注*/
    # 净利润
    netProfit = Float()
    # 少数股东权益
    minorityBookValue = Float()
    # 未确认的投资损失
    unrealisedInvestmentLosses = Float()
    # 资产减值准备
    allowanceForAssetDevaluation = Float()
    # 固定资产折旧、油气资产折耗、生产性物资折旧
    depreciationOfFixedAssets = Float()
    # 无形资产摊销
    amorizationOfIntangibleAssets = Float()
    # 长期待摊费用摊销
    longTermDeferredExpenses = Float()
    # 待摊费用的减少
    decreaseOfDeferredExpenses = Float()
    # 预提费用的增加
    IncreaseOfwithholdingExpenses = Float()
    # 处置固定资产、无形资产和其他长期资产的损失
    lossOnDisposalOfFixedAssets = Float()
    # 固定资产报废损失
    lossOnFixedAssetsDamaged = Float()
    # 公允价值变动损失
    lossOnFairValueChange = Float()
    # 递延收益增加（减：减少）
    changeOnDeferredRevenue = Float()
    # 预计负债
    estimatedLiabilities = Float()
    # 财务费用
    financingExpenses = Float()
    # 投资损失
    investmentLoss = Float()
    # 递延所得税资产减少
    decreaseOnDeferredIncomeTaxAssets = Float()
    # 递延所得税负债增加
    increaseOnDeferredIncomeTaxLiabilities = Float()
    # 存货的减少
    decreaseInInventories = Float()
    # 经营性应收项目的减少
    decreaseInReceivablesUnderOperatingActivities = Float()
    # 经营性应付项目的增加
    increaseInReceivablesUnderOperatingActivities = Float()
    # 已完工尚未结算款的减少(减:增加)
    decreaseOnAmountDue = Float()
    # 已结算尚未完工款的增加(减:减少)
    increaseOnSettlementNotYetCompleted = Float()
    # 其他
    other = Float()
    # 经营活动产生现金流量净额
    netCashFlowFromOperatingActivities = Float()
    # 债务转为资本
    debtsTransferToCapital = Float()
    # 一年内到期的可转换公司债券
    oneYearDueConvertibleBonds = Float()
    # 融资租入固定资产
    financingRentToFixedAsset = Float()
    # 现金的期末余额
    cashAtTheEndOfPeriod = Float()
    # 现金的期初余额
    cashAtTheBeginningOfPeriod = Float()
    # 现金等价物的期末余额
    cashEquivalentsAtTheEndOfPeriod = Float()
    # 现金等价物的期初余额
    cashEquivalentsAtTheBeginningOfPeriod = Float()
    # 现金及现金等价物的净增加额
    netIncreaseInCashAndCashEquivalents = Float()

    class Meta:
        index = 'cash_flow_statement'
        doc_type = 'doc'
        all = MetaField(enabled=False)
```
