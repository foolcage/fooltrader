# -*- coding: utf-8 -*-
import json
import logging
import os
import time

import ccxt
import pandas as pd

from fooltrader import get_exchange_dir, get_security_list
from fooltrader.api.technical import get_latest_download_trading_date
from fooltrader.consts import CRYPTOCURRENCY_EXCHANGES, CRYPTOCURRENCY_PAIR, SECURITY_TYPE_CRYPTO
from fooltrader.contract.data_contract import KDATA_COMMON_COL
from fooltrader.contract.files_contract import get_security_meta_path, get_security_list_path, \
    get_kdata_path, get_kdata_dir
from fooltrader.utils.pd_utils import kdata_df_save
from fooltrader.utils.utils import to_time_str, is_same_date

logger = logging.getLogger(__name__)


def generate_security_item(security_type, exchange, code, name, list_date=None):
    return {
        'code': code,
        'name': name,
        'listDate': list_date,
        'timestamp': list_date,
        'exchange': exchange,
        'type': security_type,
        'id': "{}_{}_{}".format(security_type, exchange, code)
    }


def init_markets(exchanges=CRYPTOCURRENCY_EXCHANGES):
    for exchange_str in set(ccxt.exchanges) & set(exchanges):
        exchange_dir = get_exchange_dir(security_type='cryptocurrency', exchange=exchange_str)

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

                security_item = generate_security_item(security_type='cryptocurrency', exchange=exchange_str,
                                                       code=code,
                                                       name=name, list_date=None)

                kdata_dir = get_kdata_dir(security_item)

                if not os.path.exists(kdata_dir):
                    os.makedirs(kdata_dir)

                df = df.append(security_item, ignore_index=True)

                logger.info("init_markets,exchange:{} security:{}".format(exchange_str, security_item))

                if markets_type == dict:
                    security_info = markets[market]

                if markets_type == list:
                    security_info = market

                # 存储数字货币的meta信息
                if security_info:
                    with open(get_security_meta_path(security_type='cryptocurrency', exchange=exchange_str,
                                                     code=code), "w") as f:
                        json.dump(security_info, f, ensure_ascii=False)

            # 存储该交易所的数字货币列表
            if not df.empty:
                df.to_csv(get_security_list_path(security_type='cryptocurrency', exchange=exchange_str),
                          index=False)
            logger.exception("init_markets for {} success".format(exchange_str))
        except Exception as e:
            logger.exception("init_markets for {} failed".format(exchange_str), e)


def fetch_kdata(exchange_str='bitstamp'):
    ccxt_exchange = eval("ccxt.{}()".format(exchange_str))
    if ccxt_exchange.has['fetchOHLCV']:
        for _, security_item in get_security_list(security_type='cryptocurrency', exchanges=[exchange_str]).iterrows():
            try:
                if security_item['name'] not in CRYPTOCURRENCY_PAIR:
                    continue

                start_date, df = get_latest_download_trading_date(security_item)
                # 日K线只抓到昨天
                end_date = pd.Timestamp.today() - pd.DateOffset(1)

                if start_date and (start_date > end_date):
                    logger.info("{} kdata is ok".format(security_item['code']))
                    continue

                try:
                    kdatas = ccxt_exchange.fetch_ohlcv(security_item['name'], timeframe='1d')
                    # for rateLimit
                    time.sleep(5)
                except Exception as e:
                    logger.exception("fetch_kdata for {} {} failed".format(exchange_str, security_item['name']), e)
                    continue

                for kdata in kdatas:
                    timestamp = pd.Timestamp.fromtimestamp(int(kdata[0] / 1000))
                    if is_same_date(timestamp, pd.Timestamp.today()):
                        continue
                    kdata_json = {
                        'timestamp': to_time_str(timestamp),
                        'code': security_item['code'],
                        'name': security_item['name'],
                        'open': kdata[1],
                        'high': kdata[2],
                        'low': kdata[3],
                        'close': kdata[4],
                        'volume': kdata[5],
                        'securityId': security_item['id'],
                        'preClose': None,
                        'change': None,
                        'changePct': None
                    }
                    df = df.append(kdata_json, ignore_index=True)
                if not df.empty:
                    df = df.loc[:, KDATA_COMMON_COL]
                    kdata_df_save(df, get_kdata_path(security_item), calculate_change=True)
                    logger.info(
                        "fetch_kdata for exchange:{} security:{} success".format(exchange_str, security_item['name']))
            except Exception as e:
                logger.info(
                    "fetch_kdata for exchange:{} security:{} failed".format(exchange_str, security_item['name'], e))
    else:
        logger.warning("exchange:{} not support fetchOHLCV".format(exchange_str))


# not used
def fetch_tickers(exchange_str):
    exchange = eval("ccxt.{}()".format(exchange_str))
    if exchange.has['fetchTickers']:
        while True:
            tickers = exchange.fetch_tickers()
            pairs = set(tickers.keys()) & set(CRYPTOCURRENCY_PAIR)

            if not pairs:
                logger.warning("{} not support pair:{}".format(exchange_str, CRYPTOCURRENCY_PAIR))
                break

            for pair in pairs:
                ticker = tickers[pair]
                code = pair.replace('/', '-')
                tick = {
                    'timestamp': ticker['timestamp'],
                    'securityId': "{}_{}_{}".format("cryptocurrency", exchange_str, code),
                    'code': code,
                    'name': pair,
                    'price': ticker['last'],
                    'preClose': ticker['previousClose'],
                    'change': ticker['change'],
                    'changePct': ticker['percentage']
                }
                yield tick

            rate_limit = 5
            time.sleep(rate_limit)

            logger.info("fetch_tickers for {} sleep {}".format(exchange_str, rate_limit))


def _check_fetch_trades(exchange, pair):
    try:
        exchange.fetch_trades(symbol=pair, limit=1)
        return True
    except Exception as e:
        return False


def fetch_ticks(exchange_str, pairs=None):
    if not pairs:
        df = get_security_list(security_type=SECURITY_TYPE_CRYPTO, exchanges=exchange_str)
        pairs = set(df.loc[:, 'name'].tolist()) & set(CRYPTOCURRENCY_PAIR)
        if not pairs:
            logger.warning("{} not support pair:{}".format(exchange_str, CRYPTOCURRENCY_PAIR))
            return
        else:
            logger.info("{} get tick for paris:{}".format(exchange_str, pairs))

    exchange = eval("ccxt.{}()".format(exchange_str))
    if exchange.has['fetchTrades']:
        # verify one trade at first
        pairs = [pair for pair in pairs if _check_fetch_trades(exchange, pair)]

        logger.info("after check {} get tick for paris:{}".format(exchange_str, pairs))

        while True:

            for pair in pairs:
                trades = exchange.fetch_trades(symbol=pair)

                trade = trades[-1]

                code = pair.replace('/', '-')
                tick = {
                    'securityId': "{}_{}_{}".format("cryptocurrency", exchange_str, code),
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
    exchanges = ["kraken"]
    init_markets(exchanges=exchanges)
    for exchange in exchanges:
        fetch_kdata(exchange_str=exchange)
