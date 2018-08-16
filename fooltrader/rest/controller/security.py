# -*- coding: utf-8 -*-
from flask import request

from fooltrader.consts import COIN_PAIR, SECURITY_TYPE_MAP_EXCHANGES
from fooltrader.domain.data.es_quote import CoinMeta, StockMeta
from fooltrader.rest import app
from fooltrader.rest.common import success


@app.route('/security', methods=['GET'])
def get_security():
    security_type = request.args.get('securityType')
    exchange = request.args.get('exchange')

    if not exchange:
        exchange = SECURITY_TYPE_MAP_EXCHANGES[security_type]
    else:
        exchange = [exchange]

    if security_type == 'coin':
        doc_type = CoinMeta
        s = doc_type().search()
        s = s.filter('terms', exchange=exchange).filter('terms', name=COIN_PAIR)
    else:
        doc_type = StockMeta
        s = doc_type().search()

    results = s.execute()

    return success(results['hits'].to_dict())
