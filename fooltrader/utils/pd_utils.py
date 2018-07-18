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


def df_for_date_range(df, start_date=None, end_date=None):
    if start_date:
        df = df[df.index >= pd.Timestamp(start_date)]
    if end_date:
        df = df[df.index <= pd.Timestamp(end_date)]
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
