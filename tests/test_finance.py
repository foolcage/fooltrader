from fooltrader.api import fundamental


def test_get_balance_sheet_items():
    balance_sheets = fundamental.get_balance_sheet_items('600977', start_date='2016-06-30')
    assert len(balance_sheets) > 0
    for item in balance_sheets:
        assert item['totalBookValue'] > 0
        assert item['reportEventDate'] > item['reportPeriod']


def test_get_income_statement_items():
    income_statements = fundamental.get_income_statement_items('600977', start_date='2016-06-30')
    assert len(income_statements) > 0
    for item in income_statements:
        assert item['operatingRevenue'] > 0
        assert item['reportEventDate'] > item['reportPeriod']


def test_get_cash_flow_statement_items():
    cash_flow_statements = fundamental.get_cash_flow_statement_items('600977', start_date='2016-06-30')
    assert len(cash_flow_statements) > 0
    for item in cash_flow_statements:
        assert item['netCashFlowsFromOperatingActivities'] > 0
        assert item['reportEventDate'] > item['reportPeriod']
