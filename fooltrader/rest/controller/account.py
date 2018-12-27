# -*- coding: utf-8 -*-
from flask import request

from fooltrader.api.esapi import esapi
from fooltrader.rest import app
from fooltrader.rest.common import success


@app.route('/account/<trader_name>', defaults={'trader_name': None}, methods=['GET'])
def get_account(trader_name):
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    from_idx = request.args.get('from_idx', 0)
    size = request.args.get('size', 500)

    result = esapi.es_get_sim_account(trader_name=trader_name, start_date=start_date,
                                      end_date=end_date, from_idx=int(from_idx), size=int(size))

    return success(result)
