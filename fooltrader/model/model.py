# -*- coding: utf-8 -*-
from talib import abstract

SMA = abstract.Function('sma')

import enum


class TradingSignal(enum.Enum):
    TRADING_SIGNAl_LONG = 'trading_signal_long'
    TRADING_SIGNAl_SHORT = 'trading_signal_short'
    TRADING_SIGNAl_KEEP_LONG = 'trading_signal_keep_long'
    TRADING_SIGNAl_KEEP_SHORT = 'trading_signal_keep_short'


class TradingLevel(enum.Enum):
    LEVEL_1MIN = '1m'
    LEVEL_5MIN = '5m'
    LEVEL_15MIN = '15m'
    LEVEL_30MIN = '30m'
    LEVEL_1HOUR = '1h'
    LEVEL_4HOUR = '4h'
    LEVEL_1DAY = 'day'
    LEVEL_1WEEK = 'week'

    @staticmethod
    def to_ms(trading_level):
        if trading_level == TradingLevel.LEVEL_1MIN:
            return 60 * 1000
        if trading_level == TradingLevel.LEVEL_5MIN:
            return 5 * 60 * 1000
        if trading_level == TradingLevel.LEVEL_15MIN:
            return 15 * 60 * 1000
        if trading_level == TradingLevel.LEVEL_30MIN:
            return 30 * 60 * 1000
        if trading_level == TradingLevel.LEVEL_1HOUR:
            return 60 * 60 * 1000
        if trading_level == TradingLevel.LEVEL_4HOUR:
            return 4 * 60 * 60 * 1000
        if trading_level == TradingLevel.LEVEL_1DAY:
            return 24 * 60 * 60 * 1000
        if trading_level == TradingLevel.LEVEL_1WEEK:
            return 7 * 24 * 60 * 60 * 1000


class Model(object):
    history_data = None
    current_timestamp = None

    def set_history_data(self, history_data):
        self.history_data = history_data

    def append_data(self, data):
        self.history_data.append(data)
        self.current_timestamp = data['timestamp']
        self.make_decision()

    def make_decision(self):
        pass


class KdataModel(Model):
    trading_level = TradingLevel.LEVEL_1DAY

    def signal_timestamp(self):
        return self.current_timestamp + TradingLevel.to_ms(self.trading_level)


class ShortLongStatus(enum.Enum):
    SHORT_ON_LONG = 1
    LONG_ON_SHORT = -1
    SHORT_EQ_LONG = 0


class CrossMaModel(KdataModel):
    short_period = 5
    long_period = 10
    trading_level = TradingLevel.LEVEL_1DAY
    last_status = None

    # keep_status = []

    def make_decision(self):
        ma_short = SMA(self.history_data, self.short_period)[-1]
        ma_long = SMA(self.history_data, self.long_period)[-1]

        if ma_short > ma_long:
            if self.last_status == ShortLongStatus.SHORT_ON_LONG:
                return {
                    "timestamp": self.signal_timestamp(),
                    "signal": TradingSignal.TRADING_SIGNAl_KEEP_LONG
                }
            else:
                # self.keep_status.append((self.current_timestamp, ShortLongStatus.SHORT_ON_LONG))
                return {
                    "timestamp": self.signal_timestamp(),
                    "signal": TradingSignal.TRADING_SIGNAl_LONG
                }

            self.last_status = ShortLongStatus.SHORT_ON_LONG

        if ma_short < ma_long:
            if self.last_status == ShortLongStatus.LONG_ON_SHORT:
                return {
                    "timestamp": self.signal_timestamp(),
                    "signal": TradingSignal.TRADING_SIGNAl_KEEP_SHORT
                }
            else:
                # self.keep_status.append((self.current_timestamp, ShortLongStatus.LONG_ON_SHORT))
                return {
                    "timestamp": self.signal_timestamp(),
                    "signal": TradingSignal.TRADING_SIGNAl_SHORT
                }

            self.last_status = ShortLongStatus.LONG_ON_SHORT
