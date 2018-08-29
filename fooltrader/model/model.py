# -*- coding: utf-8 -*-
from talib import abstract

SMA = abstract.Function('sma')


class Model(object):
    timestamp = None
    history_data = None

    def set_context(self, timestamp, history_data):
        self.timestamp = timestamp
        self.history_data = history_data

    def make_decision(self):
        pass


class CrossMaModel(Model):
    short_ma = 5
    long_ma = 10

    def make_decision(self):
        ma_short = SMA(self.history_data, self.short_ma)[-1]
        ma_long = SMA(self.history_data, self.long_ma)[-1]

        if ma_short > ma_long:
            return 'buy'
        if ma_short < ma_long:
            return 'sell'
        return 'nothing'
