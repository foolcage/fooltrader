# -*- coding: utf-8 -*-

import json
import os

import pandas as pd

from fooltrader.contract.files_contract import get_forecast_event_path, get_event_path
from fooltrader.utils.utils import index_df_with_time


def get_forecast_items(security_item):
    """
    get forecast items.

    Parameters
    ----------
    security_item : SecurityItem or str
        the security item,id or code

    Returns
    -------
    list of json

    """
    forecast_path = get_forecast_event_path(security_item)
    if os.path.exists(forecast_path):
        with open(forecast_path) as data_file:
            forecast_json = json.load(data_file)
            return reversed(forecast_json)


def get_finance_report_event(security_item, index='reportEventDate'):
    """
    get finance report event items.

    Parameters
    ----------
    security_item : SecurityItem or str
        the security item,id or code

    index : {'reportEventDate','reportDate'} default is 'reportEventDate'
        the index for the return df

    Returns
    -------
    DataFrame

    """
    path = get_event_path(security_item, event='finance_report')

    if os.path.exists(path):
        df = pd.read_csv(path)
        df = index_df_with_time(df, index=index)
    else:
        df = pd.DataFrame()
    return df


def get_report_event_date(security_item, report_date):
    df = get_finance_report_event(security_item, index='reportDate')
    if report_date in df.index:
        se = df.loc[report_date, 'reportEventDate']
        if type(se) == str:
            return se
        else:
            return se[-1]
    else:
        return report_date
