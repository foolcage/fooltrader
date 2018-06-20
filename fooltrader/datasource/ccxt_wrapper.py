# -*- coding: utf-8 -*-
import json
import logging
import os

import ccxt
import pandas as pd

from fooltrader import get_exchange_dir, get_security_list
from fooltrader.contract.files_contract import get_security_dir, get_security_meta_path, get_security_list_path, \
    get_kdata_path
from fooltrader.utils.utils import to_time_str

logger = logging.getLogger(__name__)


def generate_security_item(security_type, exchange, code, name, list_date=None):
    return {
        'code': code,
        'name': name,
        'listDate': list_date,
        'exchange': exchange,
        'type': security_type,
        'id': "{}_{}_{}".format(security_type, exchange, code)
    }


def init_cryptocurrency_markets():
    for exchange_str in ccxt.exchanges:
        exchange_dir = get_exchange_dir(security_type='cryptocurrency', exchange=exchange_str)

        # 创建交易所目录
        if not os.path.exists(exchange_dir):
            os.makedirs(exchange_dir)

        exchange = eval("ccxt.{}()".format(exchange_str))
        try:
            markets = exchange.fetch_markets()
            df = pd.DataFrame()
            # 存储货币信息
            for name in markets:
                if 'symbol' in name:
                    name = name['symbol']
                    symbol = name.replace('/', "")
                    security_dir = get_security_dir(security_type='cryptocurrency', exchange=exchange_str,
                                                    code=symbol)
                else:
                    name = symbol
                    symbol = name.replace('/', "")

                    security_dir = get_security_dir(security_type='cryptocurrency', exchange=exchange_str,
                                                    code=symbol)

                if not os.path.exists(security_dir):
                    os.makedirs(security_dir)

                df.append(
                    generate_security_item(security_type='cryptocurrency', exchange=exchange_str, code=symbol,
                                           name=name, list_date=None), ignore_index=True)

                if type(markets) == dict:
                    security_info = markets[symbol]
                    if security_info:
                        with open(get_security_meta_path(security_type='cryptocurrency', exchange=exchange_str,
                                                         code=symbol), "w") as f:
                            json.dump(security_info, f, ensure_ascii=False)
            if not df.empty:
                df.to_csv(get_security_list_path(security_type='cryptocurrency', exchange=exchange_str))


        except Exception as e:
            logger.error("init_markets for {} failed".format(exchange_str), e)


def fetch_cryptocurrency_kdata(exchange='binance'):
    for _, security_item in get_security_list(security_type='cryptocurrency', exchange=[exchange]).iterrows():
        exchange_ccxt = eval("ccxt.{}()".format(exchange))
        if exchange_ccxt.has['fetchOHLCV']:
            kdatas = exchange_ccxt.fetch_ohlcv(security_item['code'], timeframe='1d')
            df = pd.DataFrame()

            for kdata in kdatas:
                kdata_json = {
                    'timestamp': to_time_str(kdata[0] / 1000),
                    'code': security_item['code'],
                    'open': kdata[1],
                    'high': kdata[2],
                    'low': kdata[3],
                    'close': kdata[4],
                    'volume': kdata[5],
                    'securityId': security_item['id']
                }
                df.append(kdata_json)
            df.to_csv(get_kdata_path(security_item))


if __name__ == '__main__':
    init_cryptocurrency_markets()
