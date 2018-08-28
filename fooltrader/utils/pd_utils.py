# -*- coding: utf-8 -*-
import logging
import os

import pandas as pd

from fooltrader.utils.time_utils import to_pd_timestamp

logger = logging.getLogger(__name__)


def df_save_timeseries_data(df, to_path, append=False):
    df = df.drop_duplicates(subset='timestamp', keep='last')
    df = df.set_index(df['timestamp'], drop=False)
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()

    if append and os.path.exists(to_path):
        with open(to_path, 'a') as f:
            df.to_csv(f, header=False, index=False)
    else:
        df.to_csv(to_path, index=False)


def df_for_date_range(df, start_date=None, end_date=None):
    if start_date:
        df = df[df.index >= to_pd_timestamp(start_date)]
    if end_date:
        df = df[df.index <= to_pd_timestamp(end_date)]
    return df


# we store the data always with fields:timestamp,securityId,code
def pd_read_csv(csv_path, converters=None, index='timestamp', generate_id=False):
    if converters:
        df = pd.read_csv(csv_path, converters=converters)
    else:
        df = pd.read_csv(csv_path, dtype={"code": str, 'timestamp': str})

    if not df.empty:
        # generate id if need
        if generate_id and 'id' not in df.columns and 'securityId' in df.columns and 'timestamp' in df.columns:
            df['id'] = df['securityId'] + '_' + df['timestamp']

        df = df.set_index(df[index], drop=False)

        if index == 'timestamp' or index == 'reportPeriod':
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
    return df
