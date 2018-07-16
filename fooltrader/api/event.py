# -*- coding: utf-8 -*-

import os

import pandas as pd

from fooltrader.api.quote import to_security_item
from fooltrader.contract.files_contract import get_finance_report_event_path
from fooltrader.utils.utils import index_df_with_time


def get_finance_forecast_event(security_item, start_date=None):
    """
    get forecast items.

    Parameters
    ----------
    security_item : SecurityItem or str
        the security item,id or code

    Returns
    -------
    DataFrame

    """
    security_item = to_security_item(security_item)
    path = get_finance_forecast_event(security_item)

    if os.path.exists(path):
        df = pd.read_csv(path)
        df = index_df_with_time(df)
        if start_date:
            df = df.loc[start_date:]
    else:
        df = pd.DataFrame()
    return df


def get_finance_report_event(security_item, index='timestamp', start_date=None):
    """
    get finance report event items.

    Parameters
    ----------
    security_item : SecurityItem or str
        the security item,id or code

    index : {'timestamp','reportPeriod'} default is 'timestamp'
        the index for the return df

    Returns
    -------
    DataFrame

    """
    security_item = to_security_item(security_item)
    path = get_finance_report_event_path(security_item)

    if os.path.exists(path):
        df = pd.read_csv(path)
        df = index_df_with_time(df, index=index)
        if start_date:
            df = df.loc[start_date:]

    else:
        df = pd.DataFrame()
    return df


def get_report_event_date(security_item, report_period):
    df = get_finance_report_event(security_item, index='reportPeriod')
    if report_period in df.index:
        se = df.loc[report_period, 'timestamp']
        if type(se) == str:
            return se
        else:
            return se[-1]
    else:
        return report_period
