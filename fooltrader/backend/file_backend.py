# -*- coding: utf-8 -*-
import os

import pandas as pd

from fooltrader import SECURITY_TYPE_MAP_EXCHANGES, CHINA_STOCK_SH_INDEX, USA_STOCK_NASDAQ_INDEX, CHINA_STOCK_SZ_INDEX, \
    settings, df_for_date_range
from fooltrader.backend.backend import Backend


def get_security_list_path(security_type, exchange):
    return os.path.join(settings.FOOLTRADER_STORE_PATH, security_type, '{}.csv'.format(exchange))


class FileBackend(Backend):
    def get_security_item(security_type='stock', exchange=None, code=None, start_date=None):
        df = pd.DataFrame()

        if type(exchange) == str:
            exchange = [exchange]
        if type(code) == str:
            code = [code]

        if not exchange:
            exchange = SECURITY_TYPE_MAP_EXCHANGES[security_type]

        # TODO: store them and handle in uniform way
        if security_type == 'index':
            df = df.append(pd.DataFrame(CHINA_STOCK_SH_INDEX), ignore_index=True)
            df = df.append(pd.DataFrame(CHINA_STOCK_SZ_INDEX), ignore_index=True)
            df = df.append(pd.DataFrame(USA_STOCK_NASDAQ_INDEX), ignore_index=True)
        else:
            for exchange in exchange:
                the_path = get_security_list_path(security_type, exchange)
                if os.path.exists(the_path):
                    df = df.append(pd.read_csv(the_path, dtype=str), ignore_index=True)

        if not df.empty > 0:
            df = df_for_date_range(df, start_date=start_date)

            df = df.set_index(df['code'], drop=False)
            df = df.sort_index()

            if code:
                df = df[df["code"].isin(code)]

        return df

    def get_ticks(security_item, the_date=None, start_date=None, end_date=None):
        super().get_ticks(the_date, start_date, end_date)

    def get_kdata(security_item, the_date=None, start_date=None, end_date=None, level='day'):
        super().get_kdata(the_date, start_date, end_date, level)

    def get_latest_kdata_timestamp(self, security_item):
        super().get_latest_kdata_timestamp(security_item)

    def get_latest_tick_timestamp_order(self, security_item):
        super().get_latest_tick_timestamp_order(security_item)
