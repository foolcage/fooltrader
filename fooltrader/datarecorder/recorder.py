# -*- coding: utf-8 -*-
import logging
import math
import os

import pandas as pd

from fooltrader import get_security_list, get_kdata_dir, get_tick_dir

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
            return int(math.ceil(time_delta.total_seconds() / 60))
        if level == '1h':
            return int(math.ceil(time_delta.total_seconds() / (60 * 60)))

    @staticmethod
    def init_security_dir(security_item):
        kdata_dir = get_kdata_dir(security_item)

        if not os.path.exists(kdata_dir):
            os.makedirs(kdata_dir)

        tick_dir = get_tick_dir(security_item)

        if not os.path.exists(tick_dir):
            os.makedirs(tick_dir)

    def run(self):
        logger.info("record for security_type:{} exchanges:{}".format(self.security_type, self.exchanges))

        # init security list
        # self.init_security_list()

        df = get_security_list(security_type=self.security_type, exchanges=self.exchanges,
                               codes=self.codes)

        self.security_items = [row.to_dict() for _, row in df.iterrows()]

        logger.info("record for security_items:{}".format(self.security_items))

        # tick,1m,day
        # thread_size = len(self.security_items) * 2 + 1
        #
        # ex = futures.ThreadPoolExecutor(max_workers=thread_size)
        #
        # wait_for = []
        #
        # wait_for.append(ex.submit(self.record_kdata, self.security_items, 'day'))
        #
        # for security_item in self.security_items:
        #     wait_for.append(ex.submit(self.record_kdata, [security_item], '1m'))
        #     wait_for.append(ex.submit(self.record_tick, security_item))
        #
        # for f in futures.as_completed(wait_for):
        #     print('result: {}'.format(f.result()))

        # self.record_kdata(self.security_items,'day')
        self.record_kdata(self.security_items[0], level='1m')
