# -*- coding: utf-8 -*-

import logging
import os

import pandas as pd

from fooltrader.api.event import get_report_event_date
from fooltrader.api.technical import to_security_item
from fooltrader.contract.files_contract import get_balance_sheet_path, get_income_statement_path, \
    get_cash_flow_statement_path, get_finance_path
from fooltrader.domain.data.es_finance import IncomeStatement, BalanceSheet, CashFlowStatement
from fooltrader.items import SecurityItem
from fooltrader.utils.utils import to_float, to_time_str, is_same_date, fill_doc_type

logger = logging.getLogger(__name__)


def get_balance_sheet_items(security_item, start_date=None, report_period=None, report_event_date=None,
                            return_type='json'):
    """
    get balance sheet items.

    Parameters
    ----------
    security_item : SecurityItem or str
        the security item,id or code
    start_date : TimeStamp str or TimeStamp
        start date
    report_period : TimeStamp str or TimeStamp
        the finance report period,eg.'20170331'
    report_event_date : TimeStamp str or TimeStamp
        the finance report published date
    return_type : str
        {'json','doc'},default: 'json'

    Returns
    -------
    list of BalanceSheet
    list of json
    DataFrame

    """

    security_item = to_security_item(security_item)

    path = get_balance_sheet_path(security_item)

    _download_finance_data_if_need(path, security_item['code'])

    encoding = 'GB2312'

    with open(path, encoding=encoding) as fr:
        lines = fr.readlines()

        # for idx, line in enumerate(lines):
        #     yield idx, line.split()

        reportDate = lines[0].split()[1:-1]
        # 货币资金
        moneyFunds = lines[3].split()[1:-1]
        # 交易性金融资产
        heldForTradingFinancialAssets = lines[4].split()[1:-1]
        # 衍生金融资产
        derivative = lines[5].split()[1:-1]
        # 应收票据
        billsReceivable = lines[6].split()[1:-1]
        # 应收账款
        accountsReceivable = lines[7].split()[1:-1]
        # 预付款项
        prepaidAccounts = lines[8].split()[1:-1]
        # 应收利息
        interestReceivable = lines[9].split()[1:-1]
        # 应收股利
        dividendReceivable = lines[10].split()[1:-1]
        # 其他应收款
        otherReceivables = lines[11].split()[1:-1]

        # 买入返售金融资产
        buyingBackTheSaleOfFinancialAssets = lines[12].split()[1:-1]
        # 存货
        inventory = lines[13].split()[1:-1]
        # 划分为持有待售的资产
        assetsForSale = lines[14].split()[1:-1]
        # 一年内到期的非流动资产
        nonCurrentAssetsDueWithinOneYear = lines[15].split()[1:-1]

        # 待摊费用
        unamortizedExpenditures = lines[16].split()[1:-1]
        # 待处理流动资产损益
        waitDealIntangibleAssetsLossOrIncome = lines[17].split()[1:-1]

        # 其他流动资产
        otherCurrentAssets = lines[18].split()[1:-1]
        # 流动资产合计
        totalCurrentAssets = lines[19].split()[1:-1]

        # 非流动资产

        # 发放贷款及垫款
        loansAndPaymentsOnBehalf = lines[21].split()[1:-1]

        # 可供出售金融资产
        availableForSaleFinancialAssets = lines[22].split()[1:-1]
        # 持有至到期投资
        heldToMaturityInvestment = lines[23].split()[1:-1]
        # 长期应收款
        longTermReceivables = lines[24].split()[1:-1]
        # 长期股权投资
        longTermEquityInvestment = lines[25].split()[1:-1]
        # 投资性房地产
        investmentRealEstate = lines[26].split()[1:-1]
        # 固定资产净额
        NetfixedAssets = lines[27].split()[1:-1]
        # 在建工程
        constructionInProcess = lines[28].split()[1:-1]
        # 工程物资
        engineerMaterial = lines[29].split()[1:-1]
        # 固定资产清理
        fixedAssetsInLiquidation = lines[30].split()[1:-1]
        # 生产性生物资产
        productiveBiologicalAssets = lines[31].split()[1:-1]
        # 公益性生物资产
        nonProfitLivingAssets = lines[32].split()[1:-1]
        # 油气资产
        oilAndGasAssets = lines[33].split()[1:-1]
        # 无形资产
        intangibleAssets = lines[34].split()[1:-1]
        # 开发支出
        developmentExpenditure = lines[35].split()[1:-1]
        # 商誉
        goodwill = lines[36].split()[1:-1]
        # 长期待摊费用
        longTermDeferredExpenses = lines[37].split()[1:-1]
        # 递延所得税资产
        deferredIncomeTaxAssets = lines[38].split()[1:-1]
        # 其他非流动资产
        OtherNonCurrentAssets = lines[39].split()[1:-1]
        # 非流动资产合计
        nonCurrentAssets = lines[40].split()[1:-1]
        # 资产总计
        totalAssets = lines[41].split()[1:-1]

        # / *流动负债 * /
        # 短期借款
        shortTermBorrowing = lines[43].split()[1:-1]
        # 交易性金融负债
        transactionFinancialLiabilities = lines[44].split()[1:-1]
        # 应付票据
        billsPayable = lines[45].split()[1:-1]
        # 应付账款
        accountsPayable = lines[46].split()[1:-1]
        # 预收款项
        accountsReceivedInAdvance = lines[47].split()[1:-1]
        # 应付手续费及佣金
        handlingChargesAndCommissionsPayable = lines[48].split()[1:-1]
        # 应付职工薪酬
        employeeBenefitsPayable = lines[49].split()[1:-1]
        # 应交税费
        taxesAndSurchargesPayable = lines[50].split()[1:-1]
        # 应付利息
        interestPayable = lines[51].split()[1:-1]
        # 应付股利
        dividendpayable = lines[52].split()[1:-1]
        # 其他应付款
        otherPayables = lines[53].split()[1:-1]
        # 预提费用
        withholdingExpenses = lines[54].split()[1:-1]
        # 一年内的递延收益
        deferredIncomeWithinOneYear = lines[55].split()[1:-1]
        # 应付短期债券
        shortTermDebenturesPayable = lines[56].split()[1:-1]
        # 一年内到期的非流动负债
        nonCurrentLiabilitiesMaturingWithinOneYear = lines[57].split()[1:-1]
        # 其他流动负债
        otherCurrentLiability = lines[58].split()[1:-1]
        # 流动负债合计
        totalCurrentLiabilities = lines[59].split()[1:-1]

        # / *非流动负债 * /
        # 长期借款
        LongTermBorrowing = lines[61].split()[1:-1]
        # 应付债券
        bondPayable = lines[62].split()[1:-1]
        # 长期应付款
        longTermPayables = lines[63].split()[1:-1]
        # 长期应付职工薪酬
        longTermEmployeeBenefitsPayable = lines[64].split()[1:-1]
        # 专项应付款
        specialPayable = lines[65].split()[1:-1]
        # 预计非流动负债
        expectedNonCurrentLiabilities = lines[66].split()[1:-1]
        # 递延所得税负债
        deferredIncomeTaxLiabilities = lines[67].split()[1:-1]
        # 长期递延收益
        longTermDeferredRevenue = lines[68].split()[1:-1]
        # 其他非流动负债
        otherNonCurrentLiabilities = lines[69].split()[1:-1]
        # 非流动负债合计
        totalNonCurrentLiabilities = lines[70].split()[1:-1]
        # 负债合计
        totalLiabilities = lines[71].split()[1:-1]

        # / *所有者权益 * /
        # 实收资本(或股本)
        totalShareCapital = lines[73].split()[1:-1]

        # 资本公积
        capitalSurplus = lines[74].split()[1:-1]
        # 减：库存股
        treasuryStock = lines[75].split()[1:-1]
        # 其他综合收益
        otherComprehensiveIncome = lines[76].split()[1:-1]
        # 专项储备
        theSpecialReserve = lines[77].split()[1:-1]

        # 盈余公积
        surplusReserves = lines[78].split()[1:-1]
        # 一般风险准备
        generalRiskPreparation = lines[79].split()[1:-1]
        # 未分配利润
        undistributedProfits = lines[80].split()[1:-1]
        # 归属于母公司股东权益合计(净资产)
        bookValue = lines[81].split()[1:-1]

        # 少数股东权益
        minorityBookValue = lines[82].split()[1:-1]

        # 所有者权益(或股东权益)合计
        totalBookValue = lines[83].split()[1:-1]

        # 负债和所有者权益(或股东权益)总计
        totalLiabilitiesAndOwnersEquity = lines[84].split()[1:-1]

        result_list = []
        for idx, _ in enumerate(reportDate):
            if start_date:
                if pd.Timestamp(reportDate[idx]) < pd.Timestamp(start_date):
                    continue

            reportEventDate = get_report_event_date(security_item, report_period=reportDate[idx])

            if report_period and not is_same_date(report_period, reportDate[idx]):
                continue

            # use report_event_date to filter the reportEventDate before it for not getting future data
            if report_event_date and pd.Timestamp(report_event_date) < pd.Timestamp(reportEventDate):
                continue

            the_json = {
                "id": '{}_{}'.format(security_item["id"], reportDate[idx]),
                "reportPeriod": to_time_str(reportDate[idx]),
                "timestamp": to_time_str(reportEventDate),
                "reportEventDate": to_time_str(reportEventDate),
                "securityId": security_item["id"],
                "code": security_item["code"],
                # 货币资金
                "moneyFunds": to_float(moneyFunds[idx]),
                # 交易性金融资产
                "heldForTradingFinancialAssets": to_float(heldForTradingFinancialAssets[idx]),
                # 衍生金融资产
                "derivative": to_float(derivative[idx]),
                # 应收票据
                "billsReceivable": to_float(billsReceivable[idx]),
                # 应收账款
                "accountsReceivable": to_float(accountsReceivable[idx]),
                # 预付款项
                "prepaidAccounts": to_float(prepaidAccounts[idx]),
                # 应收利息
                "interestReceivable": to_float(interestReceivable[idx]),
                # 应收股利
                "dividendReceivable": to_float(dividendReceivable[idx]),
                # 其他应收款
                "otherReceivables": to_float(otherReceivables[idx]),

                # 买入返售金融资产
                "buyingBackTheSaleOfFinancialAssets": to_float(buyingBackTheSaleOfFinancialAssets[idx]),
                # 存货
                "inventory": to_float(inventory[idx]),
                # 划分为持有待售的资产
                "assetsForSale": to_float(assetsForSale[idx]),
                # 一年内到期的非流动资产
                "nonCurrentAssetsDueWithinOneYear": to_float(nonCurrentAssetsDueWithinOneYear[idx]),

                # 待摊费用
                "unamortizedExpenditures": to_float(unamortizedExpenditures[idx]),
                # 待处理流动资产损益
                "waitDealIntangibleAssetsLossOrIncome": to_float(waitDealIntangibleAssetsLossOrIncome[idx]),

                # 其他流动资产
                "otherCurrentAssets": to_float(otherCurrentAssets[idx]),
                # 流动资产合计
                "totalCurrentAssets": to_float(totalCurrentAssets[idx]),

                # 非流动资产

                # 发放贷款及垫款
                "loansAndPaymentsOnBehalf": to_float(loansAndPaymentsOnBehalf[idx]),

                # 可供出售金融资产
                "availableForSaleFinancialAssets": to_float(availableForSaleFinancialAssets[idx]),
                # 持有至到期投资
                "heldToMaturityInvestment": to_float(heldToMaturityInvestment[idx]),
                # 长期应收款
                "longTermReceivables": to_float(longTermReceivables[idx]),
                # 长期股权投资
                "longTermEquityInvestment": to_float(longTermEquityInvestment[idx]),
                # 投资性房地产
                "investmentRealEstate": to_float(investmentRealEstate[idx]),
                # 固定资产净额
                "NetfixedAssets": to_float(NetfixedAssets[idx]),
                # 在建工程
                "constructionInProcess": to_float(constructionInProcess[idx]),
                # 工程物资
                "engineerMaterial": to_float(engineerMaterial[idx]),
                # 固定资产清理
                "fixedAssetsInLiquidation": to_float(fixedAssetsInLiquidation[idx]),
                # 生产性生物资产
                "productiveBiologicalAssets": to_float(productiveBiologicalAssets[idx]),
                # 公益性生物资产
                "nonProfitLivingAssets": to_float(nonProfitLivingAssets[idx]),
                # 油气资产
                "oilAndGasAssets": to_float(oilAndGasAssets[idx]),
                # 无形资产
                "intangibleAssets": to_float(intangibleAssets[idx]),
                # 开发支出
                "developmentExpenditure": to_float(developmentExpenditure[idx]),
                # 商誉
                "goodwill": to_float(goodwill[idx]),
                # 长期待摊费用
                "longTermDeferredExpenses": to_float(longTermDeferredExpenses[idx]),
                # 递延所得税资产
                "deferredIncomeTaxAssets": to_float(deferredIncomeTaxAssets[idx]),
                # 其他非流动资产
                "OtherNonCurrentAssets": to_float(OtherNonCurrentAssets[idx]),
                # 非流动资产合计
                "nonCurrentAssets": to_float(nonCurrentAssets[idx]),
                # 资产总计
                "totalAssets": to_float(totalAssets[idx]),

                # / *流动负债 * /
                # 短期借款
                "shortTermBorrowing": to_float(shortTermBorrowing[idx]),
                # 交易性金融负债
                "transactionFinancialLiabilities": to_float(transactionFinancialLiabilities[idx]),
                # 应付票据
                "billsPayable": to_float(billsPayable[idx]),
                # 应付账款
                "accountsPayable": to_float(accountsPayable[idx]),
                # 预收款项
                "accountsReceivedInAdvance": to_float(accountsReceivedInAdvance[idx]),
                # 应付手续费及佣金
                "handlingChargesAndCommissionsPayable": to_float(handlingChargesAndCommissionsPayable[idx]),
                # 应付职工薪酬
                "employeeBenefitsPayable": to_float(employeeBenefitsPayable[idx]),
                # 应交税费
                "taxesAndSurchargesPayable": to_float(taxesAndSurchargesPayable[idx]),
                # 应付利息
                "interestPayable": to_float(interestPayable[idx]),
                # 应付股利
                "dividendpayable": to_float(dividendpayable[idx]),
                # 其他应付款
                "otherPayables": to_float(otherPayables[idx]),
                # 预提费用
                "withholdingExpenses": to_float(withholdingExpenses[idx]),
                # 一年内的递延收益
                "deferredIncomeWithinOneYear": to_float(deferredIncomeWithinOneYear[idx]),
                # 应付短期债券
                "shortTermDebenturesPayable": to_float(shortTermDebenturesPayable[idx]),
                # 一年内到期的非流动负债
                "nonCurrentLiabilitiesMaturingWithinOneYear": to_float(nonCurrentLiabilitiesMaturingWithinOneYear[idx]),
                # 其他流动负债
                "otherCurrentLiability": to_float(otherCurrentLiability[idx]),
                # 流动负债合计
                "totalCurrentLiabilities": to_float(totalCurrentLiabilities[idx]),

                # / *非流动负债 * /
                # 长期借款
                "LongTermBorrowing": to_float(LongTermBorrowing[idx]),
                # 应付债券
                "bondPayable": to_float(bondPayable[idx]),
                # 长期应付款
                "longTermPayables": to_float(longTermPayables[idx]),
                # 长期应付职工薪酬
                "longTermEmployeeBenefitsPayable": to_float(longTermEmployeeBenefitsPayable[idx]),
                # 专项应付款
                "specialPayable": to_float(specialPayable[idx]),
                # 预计非流动负债
                "expectedNonCurrentLiabilities": to_float(expectedNonCurrentLiabilities[idx]),
                # 递延所得税负债
                "deferredIncomeTaxLiabilities": to_float(deferredIncomeTaxLiabilities[idx]),
                # 长期递延收益
                "longTermDeferredRevenue": to_float(longTermDeferredRevenue[idx]),
                # 其他非流动负债
                "otherNonCurrentLiabilities": to_float(otherNonCurrentLiabilities[idx]),
                # 非流动负债合计
                "totalNonCurrentLiabilities": to_float(totalNonCurrentLiabilities[idx]),
                # 负债合计
                "totalLiabilities": to_float(totalLiabilities[idx]),

                # / *所有者权益 * /
                # 实收资本(或股本)
                "totalShareCapital": to_float(totalShareCapital[idx]),

                # 资本公积
                "capitalSurplus": to_float(capitalSurplus[idx]),
                # 减：库存股
                "treasuryStock": to_float(treasuryStock[idx]),
                # 其他综合收益
                "otherComprehensiveIncome": to_float(otherComprehensiveIncome[idx]),
                # 专项储备
                "theSpecialReserve": to_float(theSpecialReserve[idx]),

                # 盈余公积
                "surplusReserves": to_float(surplusReserves[idx]),
                # 一般风险准备
                "generalRiskPreparation": to_float(generalRiskPreparation[idx]),
                # 未分配利润
                "undistributedProfits": to_float(undistributedProfits[idx]),
                # 归属于母公司股东权益合计(净资产)
                "bookValue": to_float(bookValue[idx]),

                # 少数股东权益
                "minorityBookValue": to_float(minorityBookValue[idx]),

                # 所有者权益(或股东权益)合计
                "totalBookValue": to_float(totalBookValue[idx]),

                # 负债和所有者权益(或股东权益)总计
                "totalLiabilitiesAndOwnersEquity": to_float(totalLiabilitiesAndOwnersEquity[idx])
            }

            the_data = the_json

            if return_type == 'doc':
                the_data = BalanceSheet(meta={'id': the_json['id']})
                fill_doc_type(the_data, the_json)

            if report_period and is_same_date(report_period, reportDate[idx]):
                return the_data

            result_list.append(the_data)

        if result_list:
            result_list = sorted(result_list, key=lambda x: pd.Timestamp(x['reportPeriod']))
        return result_list


def get_income_statement_items(security_item, start_date=None, report_period=None, report_event_date=None,
                               return_type='json'):
    """
    get income statement items.

    Parameters
    ----------
    security_item : SecurityItem or str
        the security item,id or code
    start_date : TimeStamp str or TimeStamp
        start date
    report_period : TimeStamp str or TimeStamp
        the finance report period,eg.'20170331'
    report_event_date : TimeStamp str or TimeStamp
        the finance report published date
    return_type : str
        {'json','doc'},default: 'json'

    Returns
    -------
    list of IncomeStatement
    list of json

    """

    security_item = to_security_item(security_item)

    path = get_income_statement_path(security_item)

    _download_finance_data_if_need(path, security_item['code'])

    encoding = 'GB2312'

    with open(path, encoding=encoding) as fr:
        lines = fr.readlines()
        # for idx, line in enumerate(lines):
        #     yield idx, line.split()

        reportDate = lines[0].split()[1:-1]
        # /*营业总收入*/
        # 营业收入
        operatingRevenue = lines[2].split()[1:-1]
        # /*营业总成本*/
        operatingTotalCosts = lines[4].split()[1:-1]
        # 营业成本
        operatingCosts = lines[5].split()[1:-1]
        # 营业税金及附加
        businessTaxesAndSurcharges = lines[6].split()[1:-1]
        # 销售费用
        sellingExpenses = lines[7].split()[1:-1]
        # 管理费用
        ManagingCosts = lines[8].split()[1:-1]
        # 财务费用
        financingExpenses = lines[9].split()[1:-1]
        # 资产减值损失
        assetsDevaluation = lines[10].split()[1:-1]
        # 公允价值变动收益
        incomeFromChangesInFairValue = lines[11].split()[1:-1]
        # 投资收益
        investmentIncome = lines[12].split()[1:-1]
        # 其中:对联营企业和合营企业的投资收益
        investmentIncomeFromRelatedEnterpriseAndJointlyOperating = lines[13].split()[1:-1]
        # 汇兑收益
        exchangeGains = lines[14].split()[1:-1]
        # /*营业利润*/
        operatingProfit = lines[15].split()[1:-1]
        # 加:营业外收入
        nonOperatingIncome = lines[16].split()[1:-1]
        # 减：营业外支出
        nonOperatingExpenditure = lines[17].split()[1:-1]
        # 其中：非流动资产处置损失
        disposalLossOnNonCurrentLiability = lines[18].split()[1:-1]
        # /*利润总额*/
        totalProfits = lines[19].split()[1:-1]
        # 减：所得税费用
        incomeTaxExpense = lines[20].split()[1:-1]
        # /*净利润*/
        netProfit = lines[21].split()[1:-1]
        # 归属于母公司所有者的净利润
        netProfitAttributedToParentCompanyOwner = lines[22].split()[1:-1]
        # 少数股东损益
        minorityInterestIncome = lines[23].split()[1:-1]
        # /*每股收益*/
        # 基本每股收益(元/股)
        EPS = lines[25].split()[1:-1]
        # 稀释每股收益(元/股)
        dilutedEPS = lines[26].split()[1:-1]
        # /*其他综合收益*/
        otherComprehensiveIncome = lines[27].split()[1:-1]
        # /*综合收益总额*/
        accumulatedOtherComprehensiveIncome = lines[28].split()[1:-1]
        # 归属于母公司所有者的综合收益总额
        attributableToOwnersOfParentCompany = lines[29].split()[1:-1]
        # 归属于少数股东的综合收益总额
        attributableToMinorityShareholders = lines[30].split()[1:-1]

        result_list = []
        for idx, _ in enumerate(reportDate):
            if start_date:
                if pd.Timestamp(reportDate[idx]) < pd.Timestamp(start_date):
                    continue

            if report_period and not is_same_date(report_period, reportDate[idx]):
                continue

            reportEventDate = get_report_event_date(security_item, report_period=reportDate[idx])

            # use report_event_date to filter the reportEventDate before it for not getting future data
            if report_event_date and pd.Timestamp(report_event_date) < pd.Timestamp(reportEventDate):
                continue

            the_json = {
                "id": '{}_{}'.format(security_item["id"], reportDate[idx]),
                "reportPeriod": to_time_str(reportDate[idx]),
                "timestamp": to_time_str(reportEventDate),
                "reportEventDate": to_time_str(reportEventDate),
                "securityId": security_item["id"],
                "code": security_item["code"],
                # /*营业总收入*/
                # 营业收入
                "operatingRevenue": to_float(operatingRevenue[idx]),
                # /*营业总成本*/
                "operatingTotalCosts": to_float(operatingTotalCosts[idx]),
                # 营业成本
                "operatingCosts": to_float(operatingCosts[idx]),
                # 营业税金及附加
                "businessTaxesAndSurcharges": to_float(businessTaxesAndSurcharges[idx]),
                # 销售费用
                "sellingExpenses": to_float(sellingExpenses[idx]),
                # 管理费用
                "ManagingCosts": to_float(ManagingCosts[idx]),
                # 财务费用
                "financingExpenses": to_float(financingExpenses[idx]),
                # 资产减值损失
                "assetsDevaluation": to_float(assetsDevaluation[idx]),
                # 公允价值变动收益
                "incomeFromChangesInFairValue": to_float(incomeFromChangesInFairValue[idx]),
                # 投资收益
                "investmentIncome": to_float(investmentIncome[idx]),
                # 其中:对联营企业和合营企业的投资收益
                "investmentIncomeFromRelatedEnterpriseAndJointlyOperating":
                    investmentIncomeFromRelatedEnterpriseAndJointlyOperating[idx],
                # 汇兑收益
                "exchangeGains": to_float(exchangeGains[idx]),
                # /*营业利润*/
                "operatingProfit": to_float(operatingProfit[idx]),
                # 加:营业外收入
                "nonOperatingIncome": to_float(nonOperatingIncome[idx]),
                # 减：营业外支出
                "nonOperatingExpenditure": to_float(nonOperatingExpenditure[idx]),
                # 其中：非流动资产处置损失
                "disposalLossOnNonCurrentLiability": to_float(disposalLossOnNonCurrentLiability[idx]),
                # /*利润总额*/
                "totalProfits": to_float(totalProfits[idx]),
                # 减：所得税费用
                "incomeTaxExpense": to_float(incomeTaxExpense[idx]),
                # /*净利润*/
                "netProfit": to_float(netProfit[idx]),
                # 归属于母公司所有者的净利润
                "netProfitAttributedToParentCompanyOwner": to_float(netProfitAttributedToParentCompanyOwner[idx]),
                # 少数股东损益
                "minorityInterestIncome": to_float(minorityInterestIncome[idx]),
                # /*每股收益*/
                # 基本每股收益(元/股)
                "EPS": to_float(EPS[idx]),
                # 稀释每股收益(元/股)
                "dilutedEPS": to_float(dilutedEPS[idx]),
                # /*其他综合收益*/
                "otherComprehensiveIncome": to_float(otherComprehensiveIncome[idx]),
                # /*综合收益总额*/
                "accumulatedOtherComprehensiveIncome": to_float(accumulatedOtherComprehensiveIncome[idx]),
                # 归属于母公司所有者的综合收益总额
                "attributableToOwnersOfParentCompany": to_float(attributableToOwnersOfParentCompany[idx]),
                # 归属于少数股东的综合收益总额
                "attributableToMinorityShareholders": to_float(attributableToMinorityShareholders[idx])
            }

            the_data = the_json

            if return_type == 'doc':
                the_data = IncomeStatement(meta={'id': the_json['id']})
                fill_doc_type(the_data, the_json)

            if report_period and is_same_date(report_period, reportDate[idx]):
                return the_data

            result_list.append(the_data)

        if result_list:
            result_list = sorted(result_list, key=lambda x: pd.Timestamp(x['reportPeriod']))
        return result_list


def get_cash_flow_statement_items(security_item, start_date=None, report_period=None, report_event_date=None,
                                  return_type='json'):
    """
    get cash flow statement items.

    Parameters
    ----------
    security_item : SecurityItem or str
        the security item,id or code
    start_date : TimeStamp str or TimeStamp
        start date
    report_period : TimeStamp str or TimeStamp
        the finance report period,eg.'20170331'
    report_event_date : TimeStamp str or TimeStamp
        the finance report published date
    return_type : str
        {'json','doc'},default: 'json'

    Returns
    -------
    list of CashFlowStatement
    list of json

    """

    security_item = to_security_item(security_item)

    path = get_cash_flow_statement_path(security_item)

    _download_finance_data_if_need(path, security_item['code'])

    encoding = 'GB2312'

    with open(path, encoding=encoding) as fr:
        lines = fr.readlines()
        # for idx, line in enumerate(lines):
        #     yield idx, line.split()
        reportDate = lines[0].split()[1:-1]
        # /*一、经营活动产生的现金流量*/
        # 销售商品、提供劳务收到的现金
        cashFromSellingCommoditiesOrOfferingLabor = lines[3].split()[1:-1]
        # 收到的税费返还
        refundOfTaxAndFeeReceived = lines[4].split()[1:-1]
        # 收到的其他与经营活动有关的现金
        cashReceivedRelatingToOtherOperatingActivities = lines[5].split()[1:-1]
        # 经营活动现金流入小计
        subTotalOfCashInflowsFromOperatingActivities = lines[6].split()[1:-1]
        # 购买商品、接受劳务支付的现金
        cashPaidForGoodsAndServices = lines[7].split()[1:-1]
        # 支付给职工以及为职工支付的现金
        cashPaidToAndOnBehalfOfemployees = lines[8].split()[1:-1]
        # 支付的各项税费
        paymentsOfTaxesAndSurcharges = lines[9].split()[1:-1]
        # 支付的其他与经营活动有关的现金
        cashPaidRelatingToOtherOperatingActivities = lines[10].split()[1:-1]
        # 经营活动现金流出小计
        subTotalOfCashOutflowsFromOperatingActivities = lines[11].split()[1:-1]
        # 经营活动产生的现金流量净额
        netCashFlowsFromOperatingActivities = lines[12].split()[1:-1]
        # /*二、投资活动产生的现金流量*/
        # 收回投资所收到的现金
        cashReceivedFromDisposalOfInvestments = lines[14].split()[1:-1]
        # 取得投资收益所收到的现金
        cashReceivedFromReturnsOnIvestments = lines[15].split()[1:-1]
        # 处置固定资产、无形资产和其他长期资产所收回的现金净额
        netCashReceivedFromDisposalAssets = lines[16].split()[1:-1]
        # 处置子公司及其他营业单位收到的现金净额
        netCashReceivedFromDisposalSubsidiaries = lines[17].split()[1:-1]
        # 收到的其他与投资活动有关的现金
        cashReceivedFromOtherInvesting = lines[18].split()[1:-1]
        # 投资活动现金流入小计
        subTotalOfCashInflowsFromInvesting = lines[19].split()[1:-1]
        # 购建固定资产、无形资产和其他长期资产所支付的现金
        cashPaidToAcquireFixedAssets = lines[20].split()[1:-1]
        # 投资所支付的现金
        cashPaidToAcquireInvestments = lines[21].split()[1:-1]
        # 取得子公司及其他营业单位支付的现金净额
        netCashPaidToAcquireSubsidiaries = lines[22].split()[1:-1]
        # 支付的其他与投资活动有关的现金
        cashPaidRelatingToOtherInvesting = lines[23].split()[1:-1]
        # 投资活动现金流出小计
        subTotalOfCashOutflowsFromInvesting = lines[24].split()[1:-1]
        # 投资活动产生的现金流量净额
        netCashFlowsFromInvesting = lines[25].split()[1:-1]
        # /*三、筹资活动产生的现金流量*/
        # 吸收投资收到的现金
        cashReceivedFromCapitalContributions = lines[27].split()[1:-1]
        # 其中：子公司吸收少数股东投资收到的现金
        cashReceivedFromMinorityShareholdersOfSubsidiaries = lines[28].split()[1:-1]
        # 取得借款收到的现金
        cashReceivedFromBorrowings = lines[29].split()[1:-1]
        # 发行债券收到的现金
        cashReceivedFromIssuingBonds = lines[30].split()[1:-1]
        # 收到其他与筹资活动有关的现金
        cashReceivedRelatingToOtherFinancingActivities = lines[31].split()[1:-1]
        # 筹资活动现金流入小计
        subTotalOfCashInflowsFromFinancingActivities = lines[32].split()[1:-1]
        # 偿还债务支付的现金
        cashRepaymentsOfBorrowings = lines[33].split()[1:-1]
        # 分配股利、利润或偿付利息所支付的现金
        cashPaymentsForInterestExpensesAndDistributionOfDividendsOrProfits = lines[34].split()[1:-1]
        # 其中：子公司支付给少数股东的股利、利润
        cashPaymentsForDividendsOrProfitToMinorityShareholders = lines[35].split()[1:-1]
        # 支付其他与筹资活动有关的现金
        cashPaymentsRelatingToOtherFinancingActivities = lines[36].split()[1:-1]
        # 筹资活动现金流出小计
        subTotalOfCashOutflowsFromFinancingActivities = lines[37].split()[1:-1]
        # 筹资活动产生的现金流量净额
        netCashFlowsFromFinancingActivities = lines[38].split()[1:-1]
        # /*四、汇率变动对现金及现金等价物的影响*/
        effectOfForeignExchangeRate = lines[39].split()[1:-1]
        # /*五、现金及现金等价物净增加额*/
        netIncreaseInCash = lines[40].split()[1:-1]
        # 加:期初现金及现金等价物余额
        cashAtBeginningOfyear = lines[41].split()[1:-1]
        # /*六、期末现金及现金等价物余额*/
        cashAtEndOfyear = lines[42].split()[1:-1]
        # /*附注*/
        # 净利润
        netProfit = lines[44].split()[1:-1]
        # 少数股东权益
        minorityBookValue = lines[45].split()[1:-1]
        # 未确认的投资损失
        unrealisedInvestmentLosses = lines[46].split()[1:-1]
        # 资产减值准备
        allowanceForAssetDevaluation = lines[47].split()[1:-1]
        # 固定资产折旧、油气资产折耗、生产性物资折旧
        depreciationOfFixedAssets = lines[48].split()[1:-1]
        # 无形资产摊销
        amorizationOfIntangibleAssets = lines[49].split()[1:-1]
        # 长期待摊费用摊销
        longTermDeferredExpenses = lines[50].split()[1:-1]
        # 待摊费用的减少
        decreaseOfDeferredExpenses = lines[51].split()[1:-1]
        # 预提费用的增加
        IncreaseOfwithholdingExpenses = lines[52].split()[1:-1]
        # 处置固定资产、无形资产和其他长期资产的损失
        lossOnDisposalOfFixedAssets = lines[53].split()[1:-1]
        # 固定资产报废损失
        lossOnFixedAssetsDamaged = lines[54].split()[1:-1]
        # 公允价值变动损失
        lossOnFairValueChange = lines[55].split()[1:-1]
        # 递延收益增加（减：减少）
        changeOnDeferredRevenue = lines[56].split()[1:-1]
        # 预计负债
        estimatedLiabilities = lines[57].split()[1:-1]
        # 财务费用
        financingExpenses = lines[58].split()[1:-1]
        # 投资损失
        investmentLoss = lines[59].split()[1:-1]
        # 递延所得税资产减少
        decreaseOnDeferredIncomeTaxAssets = lines[60].split()[1:-1]
        # 递延所得税负债增加
        increaseOnDeferredIncomeTaxLiabilities = lines[61].split()[1:-1]
        # 存货的减少
        decreaseInInventories = lines[62].split()[1:-1]
        # 经营性应收项目的减少
        decreaseInReceivablesUnderOperatingActivities = lines[63].split()[1:-1]
        # 经营性应付项目的增加
        increaseInReceivablesUnderOperatingActivities = lines[64].split()[1:-1]
        # 已完工尚未结算款的减少(减:增加)
        decreaseOnAmountDue = lines[65].split()[1:-1]
        # 已结算尚未完工款的增加(减:减少)
        increaseOnSettlementNotYetCompleted = lines[66].split()[1:-1]
        # 其他
        other = lines[67].split()[1:-1]
        # 经营活动产生现金流量净额
        netCashFlowFromOperatingActivities = lines[68].split()[1:-1]
        # 债务转为资本
        debtsTransferToCapital = lines[69].split()[1:-1]
        # 一年内到期的可转换公司债券
        oneYearDueConvertibleBonds = lines[70].split()[1:-1]
        # 融资租入固定资产
        financingRentToFixedAsset = lines[71].split()[1:-1]
        # 现金的期末余额
        cashAtTheEndOfPeriod = lines[72].split()[1:-1]
        # 现金的期初余额
        cashAtTheBeginningOfPeriod = lines[73].split()[1:-1]
        # 现金等价物的期末余额
        cashEquivalentsAtTheEndOfPeriod = lines[74].split()[1:-1]
        # 现金等价物的期初余额
        cashEquivalentsAtTheBeginningOfPeriod = lines[75].split()[1:-1]
        # 现金及现金等价物的净增加额
        netIncreaseInCashAndCashEquivalents = lines[76].split()[1:-1]
        result_list = []
        for idx, _ in enumerate(reportDate):
            if start_date:
                if pd.Timestamp(reportDate[idx]) < pd.Timestamp(start_date):
                    continue

            if report_period and not is_same_date(report_period, reportDate[idx]):
                continue

            reportEventDate = get_report_event_date(security_item, report_period=reportDate[idx])

            # use report_event_date to filter the reportEventDate before it for not getting future data
            if report_event_date and pd.Timestamp(report_event_date) < pd.Timestamp(reportEventDate):
                continue

            the_json = {
                "id": '{}_{}'.format(security_item["id"], reportDate[idx]),
                "reportPeriod": to_time_str(reportDate[idx]),
                "timestamp": to_time_str(reportEventDate),
                "reportEventDate": to_time_str(reportEventDate),
                "securityId": security_item["id"],
                "code": security_item["code"],
                # /*一、经营活动产生的现金流量*/
                # 销售商品、提供劳务收到的现金
                "cashFromSellingCommoditiesOrOfferingLabor": to_float(cashFromSellingCommoditiesOrOfferingLabor[idx]),
                # 收到的税费返还
                "refundOfTaxAndFeeReceived": to_float(refundOfTaxAndFeeReceived[idx]),
                # 收到的其他与经营活动有关的现金
                "cashReceivedRelatingToOtherOperatingActivities": to_float(
                    cashReceivedRelatingToOtherOperatingActivities[idx]),
                # 经营活动现金流入小计
                "subTotalOfCashInflowsFromOperatingActivities": to_float(
                    subTotalOfCashInflowsFromOperatingActivities[idx]),
                # 购买商品、接受劳务支付的现金
                "cashPaidForGoodsAndServices": to_float(cashPaidForGoodsAndServices[idx]),
                # 支付给职工以及为职工支付的现金
                "cashPaidToAndOnBehalfOfemployees": to_float(cashPaidToAndOnBehalfOfemployees[idx]),
                # 支付的各项税费
                "paymentsOfTaxesAndSurcharges": to_float(paymentsOfTaxesAndSurcharges[idx]),
                # 支付的其他与经营活动有关的现金
                "cashPaidRelatingToOtherOperatingActivities": to_float(cashPaidRelatingToOtherOperatingActivities[idx]),
                # 经营活动现金流出小计
                "subTotalOfCashOutflowsFromOperatingActivities": to_float(
                    subTotalOfCashOutflowsFromOperatingActivities[idx]),
                # 经营活动产生的现金流量净额
                "netCashFlowsFromOperatingActivities": to_float(netCashFlowsFromOperatingActivities[idx]),
                # /*二、投资活动产生的现金流量*/
                # 收回投资所收到的现金
                "cashReceivedFromDisposalOfInvestments": to_float(cashReceivedFromDisposalOfInvestments[idx]),
                # 取得投资收益所收到的现金
                "cashReceivedFromReturnsOnIvestments": to_float(cashReceivedFromReturnsOnIvestments[idx]),
                # 处置固定资产、无形资产和其他长期资产所收回的现金净额
                "netCashReceivedFromDisposalAssets": to_float(netCashReceivedFromDisposalAssets[idx]),
                # 处置子公司及其他营业单位收到的现金净额
                "netCashReceivedFromDisposalSubsidiaries": to_float(netCashReceivedFromDisposalSubsidiaries[idx]),
                # 收到的其他与投资活动有关的现金
                "cashReceivedFromOtherInvesting": to_float(cashReceivedFromOtherInvesting[idx]),
                # 投资活动现金流入小计
                "subTotalOfCashInflowsFromInvesting": to_float(subTotalOfCashInflowsFromInvesting[idx]),
                # 购建固定资产、无形资产和其他长期资产所支付的现金
                "cashPaidToAcquireFixedAssets": to_float(cashPaidToAcquireFixedAssets[idx]),
                # 投资所支付的现金
                "cashPaidToAcquireInvestments": to_float(cashPaidToAcquireInvestments[idx]),
                # 取得子公司及其他营业单位支付的现金净额
                "netCashPaidToAcquireSubsidiaries": to_float(netCashPaidToAcquireSubsidiaries[idx]),
                # 支付的其他与投资活动有关的现金
                "cashPaidRelatingToOtherInvesting": to_float(cashPaidRelatingToOtherInvesting[idx]),
                # 投资活动现金流出小计
                "subTotalOfCashOutflowsFromInvesting": to_float(subTotalOfCashOutflowsFromInvesting[idx]),
                # 投资活动产生的现金流量净额
                "netCashFlowsFromInvesting": to_float(netCashFlowsFromInvesting[idx]),
                # /*三、筹资活动产生的现金流量*/
                # 吸收投资收到的现金
                "cashReceivedFromCapitalContributions": to_float(cashReceivedFromCapitalContributions[idx]),
                # 其中：子公司吸收少数股东投资收到的现金
                "cashReceivedFromMinorityShareholdersOfSubsidiaries":
                    cashReceivedFromMinorityShareholdersOfSubsidiaries[
                        idx],
                # 取得借款收到的现金
                "cashReceivedFromBorrowings": to_float(cashReceivedFromBorrowings[idx]),
                # 发行债券收到的现金
                "cashReceivedFromIssuingBonds": to_float(cashReceivedFromIssuingBonds[idx]),
                # 收到其他与筹资活动有关的现金
                "cashReceivedRelatingToOtherFinancingActivities": to_float(
                    cashReceivedRelatingToOtherFinancingActivities[idx]),
                # 筹资活动现金流入小计
                "subTotalOfCashInflowsFromFinancingActivities": to_float(
                    subTotalOfCashInflowsFromFinancingActivities[idx]),
                # 偿还债务支付的现金
                "cashRepaymentsOfBorrowings": to_float(cashRepaymentsOfBorrowings[idx]),
                # 分配股利、利润或偿付利息所支付的现金
                "cashPaymentsForInterestExpensesAndDistributionOfDividendsOrProfits":
                    cashPaymentsForInterestExpensesAndDistributionOfDividendsOrProfits[idx],
                # 其中：子公司支付给少数股东的股利、利润
                "cashPaymentsForDividendsOrProfitToMinorityShareholders":
                    cashPaymentsForDividendsOrProfitToMinorityShareholders[idx],
                # 支付其他与筹资活动有关的现金
                "cashPaymentsRelatingToOtherFinancingActivities": to_float(
                    cashPaymentsRelatingToOtherFinancingActivities[idx]),
                # 筹资活动现金流出小计
                "subTotalOfCashOutflowsFromFinancingActivities": to_float(
                    subTotalOfCashOutflowsFromFinancingActivities[idx]),
                # 筹资活动产生的现金流量净额
                "netCashFlowsFromFinancingActivities": to_float(netCashFlowsFromFinancingActivities[idx]),
                # /*四、汇率变动对现金及现金等价物的影响*/
                "effectOfForeignExchangeRate": to_float(effectOfForeignExchangeRate[idx]),
                # /*五、现金及现金等价物净增加额*/
                "netIncreaseInCash": to_float(netIncreaseInCash[idx]),
                # 加:期初现金及现金等价物余额
                "cashAtBeginningOfyear": to_float(cashAtBeginningOfyear[idx]),
                # /*六、期末现金及现金等价物余额*/
                "cashAtEndOfyear": to_float(cashAtEndOfyear[idx]),
                # /*附注*/
                # 净利润
                "netProfit": to_float(netProfit[idx]),
                # 少数股东权益
                "minorityBookValue": to_float(minorityBookValue[idx]),
                # 未确认的投资损失
                "unrealisedInvestmentLosses": to_float(unrealisedInvestmentLosses[idx]),
                # 资产减值准备
                "allowanceForAssetDevaluation": to_float(allowanceForAssetDevaluation[idx]),
                # 固定资产折旧、油气资产折耗、生产性物资折旧
                "depreciationOfFixedAssets": to_float(depreciationOfFixedAssets[idx]),
                # 无形资产摊销
                "amorizationOfIntangibleAssets": to_float(amorizationOfIntangibleAssets[idx]),
                # 长期待摊费用摊销
                "longTermDeferredExpenses": to_float(longTermDeferredExpenses[idx]),
                # 待摊费用的减少
                "decreaseOfDeferredExpenses": to_float(decreaseOfDeferredExpenses[idx]),
                # 预提费用的增加
                "IncreaseOfwithholdingExpenses": to_float(IncreaseOfwithholdingExpenses[idx]),
                # 处置固定资产、无形资产和其他长期资产的损失
                "lossOnDisposalOfFixedAssets": to_float(lossOnDisposalOfFixedAssets[idx]),
                # 固定资产报废损失
                "lossOnFixedAssetsDamaged": to_float(lossOnFixedAssetsDamaged[idx]),
                # 公允价值变动损失
                "lossOnFairValueChange": to_float(lossOnFairValueChange[idx]),
                # 递延收益增加（减：减少）
                "changeOnDeferredRevenue": to_float(changeOnDeferredRevenue[idx]),
                # 预计负债
                "estimatedLiabilities": to_float(estimatedLiabilities[idx]),
                # 财务费用
                "financingExpenses": to_float(financingExpenses[idx]),
                # 投资损失
                "investmentLoss": to_float(investmentLoss[idx]),
                # 递延所得税资产减少
                "decreaseOnDeferredIncomeTaxAssets": to_float(decreaseOnDeferredIncomeTaxAssets[idx]),
                # 递延所得税负债增加
                "increaseOnDeferredIncomeTaxLiabilities": to_float(increaseOnDeferredIncomeTaxLiabilities[idx]),
                # 存货的减少
                "decreaseInInventories": to_float(decreaseInInventories[idx]),
                # 经营性应收项目的减少
                "decreaseInReceivablesUnderOperatingActivities": to_float(
                    decreaseInReceivablesUnderOperatingActivities[idx]),
                # 经营性应付项目的增加
                "increaseInReceivablesUnderOperatingActivities": to_float(
                    increaseInReceivablesUnderOperatingActivities[idx]),
                # 已完工尚未结算款的减少(减:增加)
                "decreaseOnAmountDue": to_float(decreaseOnAmountDue[idx]),
                # 已结算尚未完工款的增加(减:减少)
                "increaseOnSettlementNotYetCompleted": to_float(increaseOnSettlementNotYetCompleted[idx]),
                # 其他
                "other": to_float(other[idx]),
                # 经营活动产生现金流量净额
                "netCashFlowFromOperatingActivities": to_float(netCashFlowFromOperatingActivities[idx]),
                # 债务转为资本
                "debtsTransferToCapital": to_float(debtsTransferToCapital[idx]),
                # 一年内到期的可转换公司债券
                "oneYearDueConvertibleBonds": to_float(oneYearDueConvertibleBonds[idx]),
                # 融资租入固定资产
                "financingRentToFixedAsset": to_float(financingRentToFixedAsset[idx]),
                # 现金的期末余额
                "cashAtTheEndOfPeriod": to_float(cashAtTheEndOfPeriod[idx]),
                # 现金的期初余额
                "cashAtTheBeginningOfPeriod": to_float(cashAtTheBeginningOfPeriod[idx]),
                # 现金等价物的期末余额
                "cashEquivalentsAtTheEndOfPeriod": to_float(cashEquivalentsAtTheEndOfPeriod[idx]),
                # 现金等价物的期初余额
                "cashEquivalentsAtTheBeginningOfPeriod": to_float(cashEquivalentsAtTheBeginningOfPeriod[idx]),
                # 现金及现金等价物的净增加额
                "netIncreaseInCashAndCashEquivalents": to_float(netIncreaseInCashAndCashEquivalents[idx])
            }

            the_data = the_json

            if return_type == 'doc':
                the_data = CashFlowStatement(meta={'id': the_json['id']})
                fill_doc_type(the_data, the_json)

            if report_period and is_same_date(report_period, reportDate[idx]):
                return the_data

            result_list.append(the_data)

        if result_list:
            result_list = sorted(result_list, key=lambda x: pd.Timestamp(x['reportPeriod']))
        return result_list


def get_finance_summary_items(security_item, start_date=None, report_period=None):
    path = get_finance_path(security_item)
    if not os.path.exists(path):
        return pd.DataFrame()

    df = pd.read_csv(path)

    if start_date:
        df = df[df["reportDate"] >= start_date]
        return df

    if report_period:
        return df[df["reportDate"] == report_period]
    return df


def _download_finance_data_if_need(the_path, the_code):
    if not os.path.exists(the_path):
        from fooltrader.datamanager.china_stock_manager import crawl_finance_data
        logger.info("try to download the finance data at first")
        crawl_finance_data(start_code=the_code, end_code=the_code)


if __name__ == '__main__':
    print(get_income_statement_items('300027', return_type='doc'))
    print(get_balance_sheet_items(
        SecurityItem(type='stock', code='300027', exchange='sz', id='stock_sz_300027'), return_type='doc'))
    print(get_cash_flow_statement_items(
        SecurityItem(type='stock', code='300027', exchange='sz', id='stock_sz_300027'), return_type='doc'))
    print(get_income_statement_items(
        SecurityItem(type='stock', code='300027', exchange='sz', id='stock_sz_300027')))
    print(get_balance_sheet_items(
        SecurityItem(type='stock', code='300027', exchange='sz', id='stock_sz_300027')))
    print(get_cash_flow_statement_items(
        SecurityItem(type='stock', code='300027', exchange='sz', id='stock_sz_300027')))
    #
    # print(get_cash_flow_statement_items(
    #     SecurityItem(type='stock', code='000338', exchange='sz', id='stock_sz_000338'), report_event_date='20170930'))
    # print(get_balance_sheet_items(
    #     SecurityItem(type='stock', code='000338', exchange='sz', id='stock_sz_000338'), report_event_date='20170930'))
    # print(get_income_statement_items(
    #     SecurityItem(type='stock', code='000338', exchange='sz', id='stock_sz_000338'), report_event_date='20170930'))

    # print(get_finance_summary_items(SecurityItem(type='stock', code='MSFT', exchange='nasdaq', id='stock_nasdaq_MSFT'),
    #                                 report_period='2016-12-31'))
