# -*- coding: utf-8 -*-
import enum

from talib import abstract

from fooltrader.trader.common import TradingSignal, TradingSignalType
from fooltrader.trader.model import Model, ModelType

SMA = abstract.Function('sma')


class ShortLongStatus(enum.Enum):
    SHORT_ON_LONG = 1
    LONG_ON_SHORT = -1
    SHORT_EQ_LONG = 0


class CrossMaModel(Model):
    short_period = 5
    long_period = 10
    last_status = None
    model_type = ModelType.TECHNICAL_MODEL

    # keep_status = []

    def make_decision(self):
        self.current_trading_signal = None
        if len(self.history_data) < 10:
            return
        ma_short = SMA(self.history_data, self.short_period)[-1]
        ma_long = SMA(self.history_data, self.long_period)[-1]

        if ma_short > ma_long:
            if self.last_status == ShortLongStatus.SHORT_ON_LONG:
                start, end = self.signal_timestamp_interval()

                self.send_trading_signal(TradingSignal(security_id=self.security_id,
                                                       current_price=self.current_data['close'],
                                                       start_timestamp=start,
                                                       end_timestamp=end,
                                                       trading_signal_type=TradingSignalType.TRADING_SIGNAl_KEEP_LONG
                                                       ))

            else:
                # self.keep_status.append((self.current_timestamp, ShortLongStatus.SHORT_ON_LONG))
                start, end = self.signal_timestamp_interval()

                self.send_trading_signal(TradingSignal(security_id=self.security_id,
                                                       current_price=self.current_data['close'],
                                                       start_timestamp=start, end_timestamp=end,
                                                       trading_signal_type=TradingSignalType.TRADING_SIGNAl_CLOSE_SHORT))

                self.send_trading_signal(TradingSignal(security_id=self.security_id,
                                                       current_price=self.current_data['close'],
                                                       start_timestamp=start, end_timestamp=end,
                                                       trading_signal_type=TradingSignalType.TRADING_SIGNAl_LONG))

            self.last_status = ShortLongStatus.SHORT_ON_LONG

        if ma_short < ma_long:
            if self.last_status == ShortLongStatus.LONG_ON_SHORT:
                start, end = self.signal_timestamp_interval()

                self.send_trading_signal(TradingSignal(security_id=self.security_id,
                                                       current_price=self.current_data['close'],
                                                       start_timestamp=start, end_timestamp=end,
                                                       trading_signal_type=TradingSignalType.TRADING_SIGNAl_KEEP_SHORT))


            else:
                # self.keep_status.append((self.current_timestamp, ShortLongStatus.LONG_ON_SHORT))
                start, end = self.signal_timestamp_interval()

                self.send_trading_signal(TradingSignal(security_id=self.security_id,
                                                       current_price=self.current_data['close'],
                                                       start_timestamp=start, end_timestamp=end,
                                                       trading_signal_type=TradingSignalType.TRADING_SIGNAl_CLOSE_LONG))

                self.send_trading_signal(TradingSignal(security_id=self.security_id,
                                                       current_price=self.current_data['close'],
                                                       start_timestamp=start, end_timestamp=end,
                                                       trading_signal_type=TradingSignalType.TRADING_SIGNAl_SHORT))

            self.last_status = ShortLongStatus.LONG_ON_SHORT
