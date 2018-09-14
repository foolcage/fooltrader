# -*- coding: utf-8 -*-
import enum

import pandas as pd

from fooltrader.api.technical import get_close_time
from fooltrader.utils.time_utils import to_pd_timestamp


class ModelType(enum.Enum):
    TECHNICAL_MODEL = 'technical_model'
    FUNDAMENTAL_MODEL = 'fundamental_model'
    NEWS_MODEL = 'news_model'


class Model(object):
    history_data = None
    current_timestamp = None
    current_data = None
    security_id = None
    trading_level = None
    model_type = None
    current_state = None
    current_trading_signal = None
    close_hour = None
    close_minute = None
    account_service = None

    def __init__(self, security_id, trading_level) -> None:
        self.security_id = security_id
        self.trading_level = trading_level
        self.close_hour, self.close_minute = get_close_time(self.security_id)

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

        if self.trading_level.is_last_data_of_day(self.close_hour, self.close_minute, self.current_timestamp):
            self.account_service.calculate_closing_account(self.current_timestamp)
            self.account_service.save_account(self.current_timestamp)

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
