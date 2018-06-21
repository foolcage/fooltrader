# -*- coding: utf-8 -*-
import json
import logging
import os

import ccxt
import pandas as pd

from fooltrader import get_exchange_dir, get_security_list
from fooltrader.api.quote import get_latest_download_trading_date
from fooltrader.contract.files_contract import get_security_meta_path, get_security_list_path, \
    get_kdata_path, get_kdata_dir
from fooltrader.utils.df_utils import kdata_df_save
from fooltrader.utils.utils import to_time_str, is_same_date

logger = logging.getLogger(__name__)

CRYPTOCURRENCY_EXCHANGES = ["binance", "okex", "huobi", "bitfinex", "bithumb", "gdax", "kraken", "hitbtc", "lbank",
                            "bitz", "bibox", "zb", "bitstamp"]


# CRYPTOCURRENCY_EXCHANGES = ["gdax", "bitstamp"]


def generate_security_item(security_type, exchange, code, name, list_date=None):
    return {
        'code': code,
        'name': name,
        'listDate': list_date,
        'exchange': exchange,
        'type': security_type,
        'id': "{}_{}_{}".format(security_type, exchange, code)
    }


def init_markets():
    for exchange_str in set(ccxt.exchanges) & set(CRYPTOCURRENCY_EXCHANGES):
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
                logger.error("unknown return markets type {}".format(markets_type))
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

        except Exception as e:
            logger.error("init_markets for {} failed".format(exchange_str), e)


def fetch_cryptocurrency_kdata(exchange_str='bitstamp'):
    for _, security_item in get_security_list(security_type='cryptocurrency', exchanges=[exchange_str]).iterrows():
        exchange = eval("ccxt.{}()".format(exchange_str))
        if exchange.has['fetchOHLCV']:
            start_date, df = get_latest_download_trading_date(security_item)
            end_date = pd.Timestamp.today() - pd.DateOffset(1)

            if start_date and (start_date > end_date):
                logger.info("{} kdata is ok".format(security_item['code']))
                return

            kdatas = exchange.fetch_ohlcv(security_item['name'], timeframe='1d')

            for kdata in kdatas:
                timestamp = pd.Timestamp.fromtimestamp(int(kdata[0] / 1000))
                if is_same_date(timestamp, pd.Timestamp.today()):
                    continue
                kdata_json = {
                    'timestamp': to_time_str(timestamp),
                    'code': security_item['code'],
                    'open': kdata[1],
                    'high': kdata[2],
                    'low': kdata[3],
                    'close': kdata[4],
                    'volume': kdata[5],
                    'securityId': security_item['id']
                }
                df = df.append(kdata_json, ignore_index=True)
            if not df.empty:
                kdata_df_save(df, get_kdata_path(security_item))


if __name__ == '__main__':
    init_markets()
    fetch_cryptocurrency_kdata(exchange_str='gdax')
