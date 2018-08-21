# -*- coding: utf-8 -*-
import json
import logging
import os
import time

import ccxt
import pandas as pd

from fooltrader import get_exchange_dir, get_security_list
from fooltrader.api.technical import get_latest_kdata_timestamp
from fooltrader.consts import COIN_EXCHANGES, COIN_PAIRS, SECURITY_TYPE_COIN
from fooltrader.contract.data_contract import KDATA_COMMON_COL
from fooltrader.contract.files_contract import get_security_meta_path, get_security_list_path, \
    get_kdata_path, get_kdata_dir
from fooltrader.datarecorder.recorder import Recorder
from fooltrader.settings import TIME_FORMAT_MICRO
from fooltrader.utils.pd_utils import kdata_df_save
from fooltrader.utils.utils import to_time_str, is_same_date, generate_security_item

logger = logging.getLogger(__name__)


class CoinRecorder(Recorder):
    security_type = 'coin'
    exchanges = set(ccxt.exchanges) & set(COIN_EXCHANGES)

    # check the exchange api to set this
    EXCHANGE_LIMIT = {
        'huobipro': {'tick_limit': 2000,
                     'kdata_limit': 2000}
    }

    def get_tick_limit(self, exchange):
        return self.EXCHANGE_LIMIT[exchange]['tick_limit']

    def get_kdata_limit(self, exchange):
        return self.EXCHANGE_LIMIT[exchange]['kdata_limit']

    def record_security(self):
        for exchange_str in self.exchanges:
            exchange_dir = get_exchange_dir(security_type=self.security_type, exchange=exchange_str)

            # 创建交易所目录
            if not os.path.exists(exchange_dir):
                os.makedirs(exchange_dir)

            exchange = eval("ccxt.{}()".format(exchange_str))
            try:
                markets = exchange.fetch_markets()
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

                    kdata_dir = get_kdata_dir(security_item)

                    if not os.path.exists(kdata_dir):
                        os.makedirs(kdata_dir)

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

    def record_kdata(self, level):
        for exchange_str in self.exchanges:
            ccxt_exchange = eval("ccxt.{}()".format(exchange_str))
            if ccxt_exchange.has['fetchOHLCV']:
                for _, security_item in get_security_list(security_type=self.security_type,
                                                          exchanges=[exchange_str]).iterrows():
                    if security_item['name'] not in COIN_PAIRS:
                        continue

                    try:
                        latest_timestamp, df = get_latest_kdata_timestamp(security_item, level)
                        size = Recorder.evaluate_kdata_size_to_now(latest_timestamp, level=level)

                        if size == 0:
                            logger.info("{} kdata is ok".format(security_item['code']))
                            continue

                        kdatas = ccxt_exchange.fetch_ohlcv(security_item['name'],
                                                           timeframe=Recorder.level_to_timeframe(level),
                                                           limit=size)

                        for kdata in kdatas:
                            timestamp = kdata[0]

                            if level == 'day' and is_same_date(timestamp, pd.Timestamp.today()):
                                continue

                            kdata_json = {
                                'timestamp': timestamp,
                                'datetime': to_time_str(timestamp, time_fmt=TIME_FORMAT_MICRO),
                                'code': security_item['code'],
                                'name': security_item['name'],
                                'open': kdata[1],
                                'high': kdata[2],
                                'low': kdata[3],
                                'close': kdata[4],
                                'volume': kdata[5],
                                'securityId': security_item['id']
                            }
                            df = df.append(kdata_json, ignore_index=True)
                        if not df.empty:
                            df = df.loc[:, KDATA_COMMON_COL]
                            kdata_df_save(df, get_kdata_path(security_item))
                            logger.info(
                                "fetch_kdata for exchange:{} security:{} success".format(exchange_str,
                                                                                         security_item['name']))
                    except Exception as e:
                        logger.info(
                            "fetch_kdata for exchange:{} security:{} failed".format(exchange_str, security_item['name'],
                                                                                    e))
            else:
                logger.warning("exchange:{} not support fetchOHLCV".format(exchange_str))

    def _check_fetch_trades(self, exchange, pair):
        try:
            exchange.fetch_trades(symbol=pair, limit=1)
            return True
        except Exception as e:
            return False

    def record_tick(self, exchange_str, pairs=None):
        if not pairs:
            df = get_security_list(security_type=SECURITY_TYPE_COIN, exchanges=exchange_str)
            pairs = set(df.loc[:, 'name'].tolist()) & set(COIN_PAIRS)
            if not pairs:
                logger.warning("{} not support pair:{}".format(exchange_str, COIN_PAIRS))
                return
            else:
                logger.info("{} get tick for paris:{}".format(exchange_str, pairs))

        exchange = eval("ccxt.{}()".format(exchange_str))
        if exchange.has['fetchTrades']:
            # verify one trade at first
            pairs = [pair for pair in pairs if self._check_fetch_trades(exchange, pair)]

            logger.info("after check {} get tick for paris:{}".format(exchange_str, pairs))

            while True:

                for pair in pairs:
                    trades = exchange.fetch_trades(symbol=pair)

                    trade = trades[-1]

                    code = pair.replace('/', '-')
                    tick = {
                        'securityId': "{}_{}_{}".format("coin", exchange_str, code),
                        'code': code,
                        'name': pair,
                        'timestamp': int(trade['timestamp'] / 1000),
                        'id': trade['id'],
                        'price': trade['price'],
                        'volume': trade['amount']
                    }
                    yield tick

                rate_limit = 5
                time.sleep(rate_limit)

                logger.info("fetch_tickers exchange:{} pairs:{} sleep:{}".format(exchange_str, pairs, rate_limit))


if __name__ == '__main__':
    pass
