# -*- coding: utf-8 -*-
import logging

import pandas as pd

logger = logging.getLogger(__name__)


def kdata_df_save(df, to_path, calculate_change=False):
    df = df.drop_duplicates(subset='timestamp', keep='last')
    df = df.set_index(df['timestamp'], drop=False)
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()

    if calculate_change:
        pre_close = None
        for index in df.index:
            try:
                if pd.notna(df.loc[index, ['preClose', 'change', 'changePct']]).all():
                    continue
                current_close = df.loc[index, 'close']
                if pre_close:
                    df.loc[index, 'preClose'] = pre_close
                    change = current_close - pre_close
                    df.loc[index, 'change'] = change
                    df.loc[index, 'changePct'] = change / current_close
                pre_close = df.loc[index, 'close']
            except  Exception as e:
                logger.exception("pre_close:{},current:{}".format(pre_close, df.loc[index, :].to_dict()), e)

    df.to_csv(to_path, index=False)


def df_for_date_range(df, start_date=None, end_date=None, timestamp_filed='timestamp'):
    if start_date or end_date:
        df[timestamp_filed] = pd.to_datetime(df[timestamp_filed])
    if start_date:
        df = df[df[timestamp_filed] >= pd.Timestamp(start_date)]
    if end_date:
        df = df[df[timestamp_filed] <= pd.Timestamp(end_date)]
    return df


def read_csv(csv_path, converters=None, index='timestamp'):
    if converters:
        df = pd.read_csv(csv_path, converters=converters)
    else:
        df = pd.read_csv(csv_path, dtype=str)

    df = df.set_index(df[index], drop=False)
    if index == 'timestamp' or index == 'reportPeriod':
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
    return df
