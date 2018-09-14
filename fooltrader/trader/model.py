# -*- coding: utf-8 -*-
import enum

import pandas as pd

from fooltrader.trader.account import SimAccountService
from fooltrader.utils.time_utils import to_pd_timestamp


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


class ModelType(enum.Enum):
    TECHNICAL_MODEL = 'technical_model'
    FUNDAMENTAL_MODEL = 'fundamental_model'
    NEWS_MODEL = 'news_model'


class TradingSignal:
    def __init__(self, security_id, start_timestamp, end_timestamp, trading_signal_type, current_price):
        self.security_id = security_id
        self.start_timestamp = start_timestamp
        self.end_timestamp = end_timestamp
        self.trading_signal_type = trading_signal_type
        self.current_price = current_price


class Model(object):
    history_data = None
    current_timestamp = None
    current_data = None
    security_id = None
    trading_level = None
    model_type = None
    current_state = None
    current_trading_signal = None
    account_service = SimAccountService()

    def __init__(self, security_id, trading_level) -> None:
        self.security_id = security_id
        self.trading_level = trading_level

    def set_history_data(self, history_data):
        self.history_data = pd.DataFrame(history_data)
        self.current_timestamp = to_pd_timestamp(history_data[-1]['timestamp'])
        self.current_data = history_data[-1]

    def append_data(self, data):
        if self.history_data is None:
            self.history_data = pd.DataFrame()

        self.history_data = self.history_data.append(data)
        self.current_timestamp = data.name
        self.current_data = data

        self.make_decision()

        self.account_service.handle_trading_signal(self.current_trading_signal)

    def evaluate_fetch_interval(self, end_timestamp):
        if not self.current_timestamp:
            self.current_timestamp = end_timestamp
            return None, None
        time_delta = end_timestamp - self.current_timestamp
        if time_delta.total_seconds() >= self.trading_level.to_second():
            return self.current_timestamp, end_timestamp
        return None, None

    def get_state(self):
        return self.current_state

    def get_trading_singal(self):
        return self.current_trading_signal

    def make_decision(self):
        pass

    def signal_timestamp_interval(self):
        return self.current_timestamp, self.current_timestamp + pd.Timedelta(seconds=self.trading_level.to_second())
