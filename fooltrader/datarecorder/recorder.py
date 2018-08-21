# -*- coding: utf-8 -*-
import pandas as pd


class Recorder(object):
    security_type = None
    exchanges = None
    symbols = None

    def record_security(self):
        pass

    def record_tick(self):
        pass

    def record_kdata(self):
        pass

    @staticmethod
    def level_to_timeframe(level):
        if level == 'day':
            return '1d'
        return level

    @staticmethod
    def evaluate_kdata_size_to_now(latest_record_timestamp, level='day'):
        time_delta = pd.Timestamp.now() - latest_record_timestamp

        if level == 'day':
            return time_delta.days - 1
        if level == '1m':
            return time_delta.total_seconds() / 60
        if level == '1h':
            return time_delta.total_seconds() / (60 * 60)
