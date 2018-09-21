# -*- coding: utf-8 -*-
import logging
import time

import pandas as pd

from fooltrader.api.esapi import esapi
from fooltrader.api.technical import to_security_item
from fooltrader.models.technical_model import CrossMaModel
from fooltrader.trader.common import TradingLevel
from fooltrader.utils.time_utils import to_pd_timestamp, now_pd_timestamp

logger = logging.getLogger(__name__)


class Trader(object):
    # backtest start time,would be now if not set
    start_timestamp = None
    # backtest end time,would not stop if not net
    end_timestamp = None

    current_timestamp = None
    # the trading level of the trader
    trading_level = None
    # trading_level of model must <= self.trading_level
    models = []
    security_item = None
    account_service = None

    history_data_size = 250
    missing_data = False

    def __init__(self) -> None:
        if self.start_timestamp:
            self.start_timestamp = to_pd_timestamp(self.start_timestamp)
            self.start_timestamp = self.trading_level.floor_timestamp(self.start_timestamp)
            self.current_timestamp = self.start_timestamp
        else:
            self.start_timestamp = now_pd_timestamp()

        if self.end_timestamp:
            self.end_timestamp = to_pd_timestamp(self.end_timestamp)

        if self.security_item:
            self.security_item = to_security_item(self.security_item)

        # init history data
        for model in self.models:
            datas = \
                esapi.es_get_kdata(self.security_item, level=model.trading_level.value,
                                   end_date=self.start_timestamp, order_type='desc', size=self.history_data_size)[
                    'data']
            if datas:
                model.set_history_data(datas)

            if not datas:
                logger.warning(
                    "to {}, {} no history data ".format(self.start_timestamp, self.security_item['id']))
            elif len(datas) < self.history_data_size:
                logger.warning(
                    "to {}, {} history data size:{}".format(self.start_timestamp, self.security_item['id'], len(datas)))

    def on_next_period(self):
        for model in self.models:
            start_timestamp, end_timestamp = model.evaluate_fetch_interval(self.current_timestamp)
            if start_timestamp and end_timestamp:
                retry_times = 10
                while retry_times > 0:
                    datas = esapi.es_get_kdata(self.security_item, level=model.trading_level.value,
                                               start_date=start_timestamp, end_date=end_timestamp)['data']
                    if not datas:
                        logger.warning(
                            "no kdata for security:{},trading_level:{},start_timestamp:{} end_timestamp:{} ".format(
                                self.security_item['id'], model.trading_level, start_timestamp, end_timestamp))
                        retry_times = -1
                        continue
                    for data in datas:
                        series_data = pd.Series(data)
                        series_data.name = to_pd_timestamp(data['timestamp'])
                        model.append_data(series_data)
                    break

    def run(self):
        while True:
            if self.end_timestamp and self.current_timestamp >= self.end_timestamp:
                return

            self.on_next_period()

            # time just add for backtest
            self.current_timestamp += pd.Timedelta(seconds=self.trading_level.to_second())

            if self.current_timestamp > now_pd_timestamp():
                delta = self.current_timestamp - now_pd_timestamp()
                time.sleep(delta.total_seconds())


class TestTrader(Trader):
    security_item = 'coin_binance_EOS-USDT'
    start_timestamp = '2018-06-28'
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
