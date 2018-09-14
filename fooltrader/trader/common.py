# -*- coding: utf-8 -*-
import enum


class TradingSignalType(enum.Enum):
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

    def is_last_data_of_day(self, hour, minute, pd_timestamp):
        if self == TradingLevel.LEVEL_1MIN:
            return pd_timestamp.hour == hour and pd_timestamp.minute + 1 == minute
        if self == TradingLevel.LEVEL_5MIN:
            return pd_timestamp.hour == hour and pd_timestamp.minute + 5 == minute
        if self == TradingLevel.LEVEL_15MIN:
            return pd_timestamp.hour == hour and pd_timestamp.minute + 15 == minute
        if self == TradingLevel.LEVEL_30MIN:
            return pd_timestamp.hour == hour and pd_timestamp.minute + 30 == minute
        if self == TradingLevel.LEVEL_1HOUR:
            return pd_timestamp.hour == hour and pd_timestamp.minute + 60 == minute
        if self == TradingLevel.LEVEL_4HOUR:
            return pd_timestamp.hour == hour and pd_timestamp.minute + 240 == minute
        if self >= TradingLevel.LEVEL_1DAY:
            return True

    def to_second(self):
        return int(self.to_ms() / 1000)

    def to_ms(self):
        if self == TradingLevel.LEVEL_1MIN:
            return 60 * 1000
        if self == TradingLevel.LEVEL_5MIN:
            return 5 * 60 * 1000
        if self == TradingLevel.LEVEL_15MIN:
            return 15 * 60 * 1000
        if self == TradingLevel.LEVEL_30MIN:
            return 30 * 60 * 1000
        if self == TradingLevel.LEVEL_1HOUR:
            return 60 * 60 * 1000
        if self == TradingLevel.LEVEL_4HOUR:
            return 4 * 60 * 60 * 1000
        if self == TradingLevel.LEVEL_1DAY:
            return 24 * 60 * 60 * 1000
        if self == TradingLevel.LEVEL_1WEEK:
            return 7 * 24 * 60 * 60 * 1000

    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.to_ms() >= other.to_ms()
        return NotImplemented

    def __gt__(self, other):

        if self.__class__ is other.__class__:
            return self.to_ms() > other.to_ms()
        return NotImplemented

    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.to_ms() <= other.to_ms()
        return NotImplemented

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.to_ms() < other.to_ms()
        return NotImplemented


class TradingSignal:
    def __init__(self, security_id, start_timestamp, end_timestamp, trading_signal_type, current_price):
        self.security_id = security_id
        self.start_timestamp = start_timestamp
        self.end_timestamp = end_timestamp
        self.trading_signal_type = trading_signal_type
        self.current_price = current_price
