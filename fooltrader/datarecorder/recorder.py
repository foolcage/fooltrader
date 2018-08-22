# -*- coding: utf-8 -*-
import logging
from concurrent import futures

import pandas as pd

from fooltrader import get_security_list

logger = logging.getLogger(__name__)


class Recorder(object):
    security_type = None
    exchanges = None
    codes = None
    security_items = None

    def __init__(self, security_type=None, exchanges=None, codes=None) -> None:
        if security_type:
            self.security_type = security_type
        if exchanges:
            self.exchanges = exchanges
        if codes:
            self.codes = codes

    def init_security_list(self):
        pass

    def record_tick(self, security_item):
        pass

    def record_kdata(self, security_items, level):
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

    def run(self):
        logger.info("record for security_type:{} exchanges:{}".format(self.security_type, self.exchanges))

        # init security list
        self.init_security_list()

        df = get_security_list(security_type=self.security_type, exchanges=self.exchanges,
                               codes=self.codes)

        self.security_items = [row.to_json() for _, row in df.iterrows()]

        logger.info("record for security_items:{}".format(self.security_items))

        # tick,1m,day
        thread_size = len(self.security_items) * 2 + 1

        ex = futures.ThreadPoolExecutor(max_workers=thread_size)

        ex.submit(self.record_kdata, self.security_items, 'day')

        for security_item in self.security_items:
            ex.submit(self.record_kdata, [security_item], '1m')
            ex.submit(self.record_tick, security_item)
