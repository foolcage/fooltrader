# -*- coding: utf-8 -*-
import time

import pandas as pd

from fooltrader.api.esapi import esapi
from fooltrader.api.technical import to_security_item
from fooltrader.models.technical_model import CrossMaModel
from fooltrader.trader.account import SimAccountService
from fooltrader.trader.common import TradingLevel

from fooltrader.utils.time_utils import to_pd_timestamp, now_pd_timestamp


class Trader(object):
    start_timestamp = None
    end_timestamp = None
    current_timestamp = None
    models = []
    trading_level = None
    security_item = None
    account_service = None

    def __init__(self) -> None:
        if self.start_timestamp:
            self.start_timestamp = to_pd_timestamp(self.start_timestamp)
            self.current_timestamp = self.start_timestamp
        if self.end_timestamp:
            self.end_timestamp = to_pd_timestamp(self.end_timestamp)

        if self.security_item:
            self.security_item = to_security_item(self.security_item)

        # init history data
        for model in self.models:
            datas = \
                esapi.es_get_kdata(self.security_item, level=model.trading_level.value,
                                   start_date=self.start_timestamp, end_date=self.current_timestamp)[
                    'data']
            if datas:
                model.set_history_data(datas)

    def on_next_period(self):
        for model in self.models:
            from_timestamp, end_timestamp = model.evaluate_fetch_interval(self.current_timestamp)
            if from_timestamp and end_timestamp:
                datas = esapi.es_get_kdata(self.security_item, level=model.trading_level.value,
                                           start_date=from_timestamp, end_date=end_timestamp)['data']
                for data in datas:
                    series_data = pd.Series(data)
                    series_data.name = to_pd_timestamp(data['timestamp'])
                    model.append_data(series_data)

    def run(self):
        while True:
            if self.end_timestamp and self.current_timestamp >= self.end_timestamp:
                return

            self.on_next_period()

            self.current_timestamp += pd.Timedelta(seconds=self.trading_level.to_second())

            if self.current_timestamp > now_pd_timestamp():
                time.sleep(10)


class TestTrader(Trader):
    security_item = 'coin_binance_EOS-USDT'
    start_timestamp = '2018-05-28'
    trading_level = TradingLevel.LEVEL_1DAY

    models = [CrossMaModel(security_id=security_item, trading_level=trading_level, trader_name='test_trader',
                           timestamp=start_timestamp)]

    def on_next_period(self):
        super().on_next_period()
        # check the models decision
        # check the models state


if __name__ == '__main__':
    test_trader = TestTrader()
    test_trader.run()
