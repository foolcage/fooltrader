# -*- coding: utf-8 -*-

from elasticsearch_dsl import DocType, Keyword, Date, MetaField
from elasticsearch_dsl import Float

from fooltrader.domain import BaseDocType


class BalanceSheet(BaseDocType):
    id = Keyword()
    securityId = Keyword()
    code = Keyword()
    reportPeriod = Date()
    timestamp = Date()
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
        dynamic = MetaField('strict')


class IncomeStatement(BaseDocType):
    id = Keyword()
    securityId = Keyword()
    code = Keyword()
    reportPeriod = Date()
    timestamp = Date()
    reportEventDate = Date()
    # /*营业总收入*/
    # 营业收入
    operatingRevenue = Float()
    # /*营业总成本*/
    operatingTotalCosts = Float()
    # 营业成本
    operatingCosts = Float()
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
        dynamic = MetaField('strict')


class CashFlowStatement(DocType):
    id = Keyword()
    securityId = Keyword()
    code = Keyword()
    reportPeriod = Date()
    timestamp = Date()
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
        dynamic = MetaField('strict')


class FinanceSummary(DocType):
    class Meta:
        index = 'finance_summary'
        doc_type = 'doc'
        all = MetaField(enabled=False)
        dynamic = MetaField('strict')

    id = Keyword()
    securityId = Keyword()
    code = Keyword()
    reportDate = Date()

    shares = Float()
    sharesAdjusted = Float()
    factor = Float()
    totalAssets = Float()
    totalCurrentAssets = Float()
    totalLiabilities = Float()
    totalCurrentLiabilities = Float()
    bookValue = Float()
    minorityBookValue = Float()
    preferredEquity = Float()
    goodwill = Float()
    longTermBorrowing = Float()
    operatingRevenue = Float()
    netProfit = Float()
    netProfitAttributedToParentCompanyOwner = Float()
    EPS = Float()
    dilutedEPS = Float()
    DPS = Float()
    netCashFlowsFromOperatingActivities = Float()
    netCashFlowsFromInvesting = Float()
    netCashFlowsFromFinancingActivities = Float()
    cashChange = Float()
    cashAtTheEndOfPeriod = Float()
    capitalExpenditures = Float()
    price = Float()
    priceHigh = Float()
    priceLow = Float()
    ROE = Float()
    ROA = Float()
    BVPS = Float()
    PB = Float()
    PE = Float()
    cumulativeDividendsPerShare = Float()
    dividendPayoutRatio = Float()
    longTermDebtToEquityRatio = Float()
    equityToAssetsRatio = Float()
    netMargin = Float()
    assetTurnover = Float()
    freeCashFlowPerShare = Float()
    currentRatio = Float()

    {"Quarter end": "timestamp",
     "Shares": "shares",
     "Shares split adjusted": "sharesAdjusted",
     "Split factor": "factor",
     "Assets": "totalAssets",
     "Current Assets": "totalCurrentAssets",
     "Liabilities": "totalLiabilities",
     "Current Liabilities": "totalCurrentLiabilities",
     "Shareholders equity": "bookValue",
     "Non-controlling interest": "minorityBookValue",
     "Preferred equity": "preferredEquity",
     "Goodwill & intangibles": "goodwill",
     "Long-term debt": "longTermBorrowing",
     "Revenue": "operatingRevenue",
     "Earnings": "netProfit",
     "Earnings available for common stockholders": "netProfitAttributedToParentCompanyOwner",
     "EPS basic": "EPS",
     "EPS diluted": "dilutedEPS",
     "Dividend per share": "DPS",
     "Cash from operating activities": "netCashFlowsFromOperatingActivities",
     "Cash from investing activities": "netCashFlowsFromInvesting",
     "Cash from financing activities": "netCashFlowsFromFinancingActivities",
     "Cash change during period": "cashChange",
     "Cash at end of period": "cashAtTheEndOfPeriod",
     "Capital expenditures": "capitalExpenditures",
     "Price": "price",
     "Price high": "priceHigh",
     "Price low": "priceLow",
     "ROE": "ROE",
     "ROA": "ROA",
     "Book value of equity per share": "BVPS",
     "P/B ratio": "PB",
     "P/E ratio": "PE",
     "Cumulative dividends per share": "cumulativeDividendsPerShare",
     "Dividend payout ratio": "dividendPayoutRatio",
     "Long-term debt to equity ratio": "longTermDebtToEquityRatio",
     "Equity to assets ratio": "equityToAssetsRatio",
     "Net margin": "netMargin",
     "Asset turnover": "assetTurnover",
     "Free cash flow per share": "freeCashFlowPerShare",
     "Current ratio": "currentRatio"}
