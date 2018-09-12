# -*- coding: utf-8 -*-
import time

from fooltrader.api.esapi import esapi
from fooltrader.api.technical import to_security_item
from fooltrader.models.technical_model import CrossMaModel
from fooltrader.trader.model import TradingLevel
from fooltrader.utils.time_utils import now_timestamp, to_pd_timestamp


class Trader(object):
    start_timestamp = None
    end_timestamp = None
    current_timestamp = None
    models = []
    trading_level = None
    security_item = None

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
            datas = esapi.es_get_kdata(self.security_item, level=model.trading_level.value,
                                       end_date=self.start_timestamp)['data']
            model.set_history_data(datas)

    def on_next_period(self):
        for model in self.models:
            from_timestamp, to_timestamp = model.evaluate_fetch_interval(self.current_timestamp)
            if from_timestamp and to_timestamp:
                datas = esapi.es_get_kdata(self.security_item, level=model.trading_level.value,
                                           start_date=from_timestamp, end_date=to_timestamp)['data']
                for data in datas:
                    model.append_data(data)

    def run(self):
        while True:
            if self.end_timestamp and self.current_timestamp >= self.end_timestamp:
                return

            self.on_next_period()

            self.current_timestamp += self.trading_level.to_ms()

            if self.current_timestamp > now_timestamp():
                time.sleep(10)


class TestTrader(Trader):
    security_item = 'stock_sz_300027'
    start_timestamp = '2009-10-30'
    end_timestamp = '2018-01-01'

    models = [CrossMaModel()]

    trading_level = TradingLevel.LEVEL_1DAY


if __name__ == '__main__':
    test_trader = TestTrader()
    test_trader.run()
