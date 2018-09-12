# -*- coding: utf-8 -*-
import enum

from talib import abstract

from fooltrader.trader.model import TradingSignal, Model, ModelType

SMA = abstract.Function('sma')


class ShortLongStatus(enum.Enum):
    SHORT_ON_LONG = 1
    LONG_ON_SHORT = -1
    SHORT_EQ_LONG = 0


class CrossMaModel(Model):
    short_period = 5
    long_period = 10
    trading_level = None
    last_status = None
    model_type = ModelType.TECHNICAL_MODEL

    def __init__(self, trading_level) -> None:
        super().__init__(trading_level)
        self.trading_level = trading_level

    # keep_status = []

    def make_decision(self):
        ma_short = SMA(self.history_data, self.short_period)[-1]
        ma_long = SMA(self.history_data, self.long_period)[-1]

        if ma_short > ma_long:
            if self.last_status == ShortLongStatus.SHORT_ON_LONG:
                yield {
                    "timestamp": self.signal_timestamp(),
                    "signal": TradingSignal.TRADING_SIGNAl_KEEP_LONG
                }
            else:
                # self.keep_status.append((self.current_timestamp, ShortLongStatus.SHORT_ON_LONG))
                yield {
                    "timestamp": self.signal_timestamp(),
                    "signal": TradingSignal.TRADING_SIGNAl_LONG
                }

            self.last_status = ShortLongStatus.SHORT_ON_LONG

        if ma_short < ma_long:
            if self.last_status == ShortLongStatus.LONG_ON_SHORT:
                yield {
                    "timestamp": self.signal_timestamp(),
                    "signal": TradingSignal.TRADING_SIGNAl_KEEP_SHORT
                }
            else:
                # self.keep_status.append((self.current_timestamp, ShortLongStatus.LONG_ON_SHORT))
                yield {
                    "timestamp": self.signal_timestamp(),
                    "signal": TradingSignal.TRADING_SIGNAl_SHORT
                }

            self.last_status = ShortLongStatus.LONG_ON_SHORT
