import json
import os

import pandas as pd

from fooltrader.contract.files_contract import get_forecast_event_path, get_event_path
from fooltrader.utils.utils import index_df_with_time


def get_forecast_items(security_item):
    forecast_path = get_forecast_event_path(security_item)
    if os.path.exists(forecast_path):
        with open(forecast_path) as data_file:
            forecast_json = json.load(data_file)
            for json_item in reversed(forecast_json):
                yield json_item


def get_finance_report_event(security_item, index='reportEventDate'):
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
        return df.loc[report_date, 'reportEventDate']
    else:
        return report_date
