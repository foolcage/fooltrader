# -*- coding: utf-8 -*-

import os

import pandas as pd

from fooltrader.api.technical import to_security_item
from fooltrader.contract.files_contract import get_event_path
from fooltrader.utils import pd_utils
from fooltrader.utils.pd_utils import df_for_date_range


def get_event(security_item, event_type='finance_forecast', start_date=None, end_date=None, index='timestamp'):
    """
    get forecast items.

    Parameters
    ----------
    security_item : SecurityItem or str
        the security item,id or code

    event_type : str
        {'finance_forecast','finance_report'}

    start_date: Timestamp str or Timestamp
        the start date for the event

    end_date: Timestamp str or Timestamp
        the end date for the event

    Returns
    -------
    DataFrame

    """
    security_item = to_security_item(security_item)
    path = get_event_path(security_item, event_type)

    if os.path.exists(path):
        df = pd_utils.pd_read_csv(path, index=index, generate_id=True)
        df = df_for_date_range(df, start_date=start_date, end_date=end_date)
    else:
        df = pd.DataFrame()

    return df


def get_finance_forecast_event(security_item, start_date=None, end_date=None):
    return get_event(security_item, event_type='finance_forecast', start_date=start_date, end_date=end_date)


def get_finance_report_event(security_item, index='timestamp', start_date=None, end_date=None):
    return get_event(security_item, event_type='finance_report', start_date=start_date, end_date=end_date, index=index)


def get_report_event_date(security_item, report_period):
    df = get_finance_report_event(security_item, index='reportPeriod')
    if report_period in df.index:
        report_event_date = df.loc[report_period, 'timestamp']
        if type(report_event_date) == pd.Series:
            report_event_date = report_event_date.iat[-1]
        return report_event_date
    else:
        return report_period
