# -*- coding: utf-8 -*-
import argparse
import json
import logging
import os
import time

import ccxt
import pandas as pd

from fooltrader import get_exchange_dir, get_latest_tick_timestamp_ids
from fooltrader.api.technical import get_latest_kdata_timestamp
from fooltrader.consts import COIN_EXCHANGES, COIN_PAIRS, COIN_CODE
from fooltrader.contract.data_contract import KDATA_COMMON_COL, COIN_TICK_COL
from fooltrader.contract.files_contract import get_security_meta_path, get_security_list_path, \
    get_kdata_path, get_tick_path
from fooltrader.datarecorder.recorder import Recorder
from fooltrader.utils.pd_utils import df_save_timeseries_data
from fooltrader.utils.time_utils import is_same_date, to_pd_timestamp, to_time_str, TIME_FORMAT_ISO8601, next_date
from fooltrader.utils.utils import generate_security_item

logger = logging.getLogger(__name__)


class CoinRecorder(Recorder):
    # check the exchange api to set this
    EXCHANGE_LIMIT = {
        'huobipro': {'tick_limit': 2000,
                     'kdata_limit': 2000}
    }

    EXCHANGE_AUTH = {
        'huobipro': {
            'apiKey': '',
            'secret': ''
        }
    }

    OVERLAPPING_SIZE = 10

    def __init__(self, exchanges=None) -> None:
        super().__init__('coin', exchanges, COIN_CODE)
        self.exchanges = set(ccxt.exchanges) & set(COIN_EXCHANGES) & set(self.exchanges)

    def get_tick_limit(self, exchange):
        return self.EXCHANGE_LIMIT[exchange]['tick_limit']

    def get_kdata_limit(self, exchange):
        return self.EXCHANGE_LIMIT[exchange]['kdata_limit']

    def get_ccxt_exchange(self, exchange_str):
        exchange = eval("ccxt.{}()".format(exchange_str))
        exchange.apiKey = self.EXCHANGE_AUTH[exchange_str]['apiKey']
        exchange.secret = self.EXCHANGE_AUTH[exchange_str]['secret']
        exchange.proxies = {'http': 'http://127.0.0.1:10081', 'https': 'http://127.0.0.1:10081'}
        return exchange

    def init_security_list(self):
        for exchange_str in self.exchanges:
            exchange_dir = get_exchange_dir(security_type=self.security_type, exchange=exchange_str)

            # 创建交易所目录
            if not os.path.exists(exchange_dir):
                os.makedirs(exchange_dir)

            ccxt_exchange = self.get_ccxt_exchange(exchange_str)
            try:
                markets = ccxt_exchange.fetch_markets()
                df = pd.DataFrame()

                # markets有些为key=symbol的dict,有些为list
                markets_type = type(markets)
                if markets_type != dict and markets_type != list:
                    logger.exception("unknown return markets type {}".format(markets_type))
                    return

                for market in markets:

                    if markets_type == dict:
                        name = market
                        code = name.replace('/', "-")

                    if markets_type == list:
                        name = market['symbol']
                        code = name.replace('/', "-")

                    if name not in COIN_PAIRS:
                        continue

                    security_item = generate_security_item(security_type=self.security_type, exchange=exchange_str,
                                                           code=code,
                                                           name=name, list_date=None)

                    Recorder.init_security_dir(security_item)

                    df = df.append(security_item, ignore_index=True)

                    logger.info("init_markets,exchange:{} security:{}".format(exchange_str, security_item['id']))

                    if markets_type == dict:
                        security_info = markets[market]

                    if markets_type == list:
                        security_info = market

                    # 存储数字货币的meta信息
                    if security_info:
                        with open(get_security_meta_path(security_type=self.security_type, exchange=exchange_str,
                                                         code=code), "w") as f:
                            json.dump(security_info, f, ensure_ascii=False)

                # 存储该交易所的数字货币列表
                if not df.empty:
                    df.to_csv(get_security_list_path(security_type=self.security_type, exchange=exchange_str),
                              index=False)
                logger.exception("init_markets for {} success".format(exchange_str))
            except Exception as e:
                logger.exception("init_markets for {} failed".format(exchange_str), e)

    def record_kdata(self, security_item, level):
        ccxt_exchange = self.get_ccxt_exchange(security_item['exchange'])

        if ccxt_exchange.has['fetchOHLCV']:
            latest_timestamp, _ = get_latest_kdata_timestamp(security_item, level=level)

            if level == 'day' and is_same_date(next_date(latest_timestamp), pd.Timestamp.today()):
                logger.info(
                    "fetch_kdata for security:{} level:{} latest_timestamp:{} success".format(security_item['id'],
                                                                                              level,
                                                                                              to_time_str(
                                                                                                  latest_timestamp)))

                return

            limit = self.get_kdata_limit(security_item['exchange'])

            if latest_timestamp:
                evaluate_size = Recorder.evaluate_kdata_size_to_now(latest_timestamp, level=level)

                # add 10 to make sure get all kdata
                if evaluate_size > limit:
                    logger.warning("evaluate_size:{},limit:{}".format(evaluate_size, limit))
                limit = min(evaluate_size + self.OVERLAPPING_SIZE, limit)

            kdata_list = []

            while True:
                try:
                    kdatas = ccxt_exchange.fetch_ohlcv(security_item['name'],
                                                       timeframe=Recorder.level_to_timeframe(level),
                                                       limit=limit)

                    has_duplicate = False

                    for kdata in kdatas:
                        current_timestamp = kdata[0]

                        if latest_timestamp and (
                                to_pd_timestamp(current_timestamp) <= to_pd_timestamp(latest_timestamp)):
                            has_duplicate = True
                            continue

                        if level == 'day' and is_same_date(current_timestamp, pd.Timestamp.today()):
                            continue

                        if level == 'day':
                            timestamp = to_time_str(current_timestamp)
                        else:
                            timestamp = to_time_str(current_timestamp, fmt=TIME_FORMAT_ISO8601)

                        kdata_json = {
                            'timestamp': timestamp,
                            'code': security_item['code'],
                            'name': security_item['name'],
                            'open': kdata[1],
                            'high': kdata[2],
                            'low': kdata[3],
                            'close': kdata[4],
                            'volume': kdata[5],
                            'securityId': security_item['id']
                        }
                        kdata_list.append(kdata_json)

                    if latest_timestamp and not has_duplicate:
                        logger.warning(
                            "{} level:{} gap between {} and {}".format(security_item['id'], level,
                                                                       to_time_str(latest_timestamp),
                                                                       to_time_str(kdatas[0][0])))
                    latest_timestamp = kdatas[-1][0]

                    if kdata_list:
                        df = pd.DataFrame(kdata_list)
                        df = df.loc[:, KDATA_COMMON_COL]

                        df_save_timeseries_data(df, get_kdata_path(security_item, level=level), append=True)
                        logger.info(
                            "fetch_kdata for security:{} level:{} latest_timestamp:{} success".format(
                                security_item['id'], level,
                                to_time_str(latest_timestamp, fmt=TIME_FORMAT_ISO8601)))
                        kdata_list = []

                    if level == 'day' and is_same_date(latest_timestamp, pd.Timestamp.today()):
                        return

                    limit = 10
                    time.sleep(self.SAFE_SLEEPING_TIME)

                except Exception as e:
                    logger.exception("record_kdata for security:{} failed".format(security_item['id']))

        else:
            logger.warning("exchange:{} not support fetchOHLCV".format(security_item['exchange']))

    def to_direction(self, side):
        if side == 'sell':
            return -1
        if side == 'buy':
            return 1
        return 0

    def record_tick(self, security_item):
        ccxt_exchange = self.get_ccxt_exchange(security_item['exchange'])

        if ccxt_exchange.has['fetchTrades']:
            latest_saved_timestamp, latest_saved_ids, _ = get_latest_tick_timestamp_ids(security_item)

            limit = self.get_tick_limit(security_item['exchange'])

            while True:
                try:
                    trades = ccxt_exchange.fetch_trades(security_item['name'], limit=limit)

                    tick_list = []
                    current_timestamp = None

                    len1 = len(trades)

                    if latest_saved_timestamp:
                        trades = [trade for trade in trades if (trade['id'] not in latest_saved_ids) and (
                                to_pd_timestamp(trade['timestamp']) >= to_pd_timestamp(latest_saved_timestamp))]

                        if len1 == len(trades):
                            logger.warning(
                                "{} level:{} gap between {} and {}".format(security_item['id'],
                                                                           to_time_str(latest_saved_timestamp,
                                                                                       TIME_FORMAT_ISO8601),
                                                                           to_time_str(trades[0]['timestamp'],
                                                                                       TIME_FORMAT_ISO8601)))

                    for trade in trades:
                        # to the next date
                        if current_timestamp and not is_same_date(current_timestamp, trade['timestamp']):
                            break

                        current_timestamp = trade['timestamp']

                        tick = {
                            'securityId': security_item['id'],
                            'id': trade['id'],
                            'order': trade['order'],
                            'timestamp': to_time_str(trade['timestamp'], TIME_FORMAT_ISO8601),
                            'datetime': trade['timestamp'],
                            'price': trade['price'],
                            'volume': trade['amount'],
                            'direction': self.to_direction(trade['side']),
                            'orderType': trade['type'],
                            'turnover': trade['price'] * trade['amount']
                        }
                        tick_list.append(tick)

                    if tick_list:
                        df = pd.DataFrame(tick_list)
                        df = df.loc[:, COIN_TICK_COL]

                        csv_path = get_tick_path(security_item, to_time_str(tick_list[0]['timestamp']))

                        df_save_timeseries_data(df, csv_path, append=True, drop_duplicate_timestamp=False)
                        logger.info(
                            "record_tick for security:{} got size:{} form {} to {} success".format(
                                security_item['id'], len(tick_list), tick_list[0]['timestamp'],
                                tick_list[-1]['timestamp']))

                        # using the saved to filter duplicate
                        latest_saved_timestamp = tick_list[-1]['timestamp']
                        latest_saved_ids = [tick['id'] for tick in tick_list if tick['id']]

                    limit = 500
                    time.sleep(10)

                except Exception as e:
                    logger.exception("record_tick for security:{} failed".format(security_item['id']))

        else:
            logger.warning("exchange:{} not support fetchTrades".format(security_item['exchange']))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # parser.add_argument('exchange', help='the exchange you want to record')

    # args = parser.parse_args()

    recorder = CoinRecorder(exchanges=['huobipro'])
    recorder.run()
