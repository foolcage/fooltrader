# -*- coding: utf-8 -*-

from fooltrader.api.fundamental import get_income_statement_items, get_balance_sheet_items


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


def check_net_profit(security_item):
    income_statement_list = get_income_statement_items(security_item=security_item)
    for income_statement in income_statement_list:
        netProfit = income_statement["totalProfits"] - income_statement["incomeTaxExpense"]
        diff = netProfit - income_statement["netProfit"]
        if abs(diff) >= 1:
            print("{} net profit calculating not pass,calculating result:{},report result:{}".format(
                income_statement['id'], netProfit, income_statement["netProfit"]))
        else:
            print("{} net profit calculating pass".format(income_statement['id']))


def check_eps(security_item):
    income_statement_list = get_income_statement_items(security_item=security_item)
    for income_statement in income_statement_list:
        balance_sheet = get_balance_sheet_items(security_item=security_item,
                                                report_period=income_statement['reportDate'])
        if not balance_sheet or balance_sheet['totalShareCapital'] == 0:
            continue

        eps = (income_statement["netProfit"] - income_statement["minorityInterestIncome"]) / (
            balance_sheet['totalShareCapital'])
        diff = eps - income_statement["EPS"]
        if abs(diff) >= 0.01:
            print("{} EPS calculating not pass,calculating result:{},report result:{}".format(
                income_statement['id'], eps, income_statement["EPS"]))
        else:
            print("{} EPS calculating pass".format(income_statement['id']))


if __name__ == '__main__':
    # check_operating_profit('000338')
    # check_net_profit('000338')
    check_eps('000338')
