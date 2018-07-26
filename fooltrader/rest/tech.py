# -*- coding: utf-8 -*-
from flask import request

from fooltrader.api.esapi import esapi
from fooltrader.rest import app
from fooltrader.rest.common import success


@app.route('/kdata/<securityid>', methods=['GET'])
def get_kdata(securityid):
    the_date = request.args.get('the_date')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    level = request.args.get('level', 'day')

    fields = request.args.get('fields')
    if not fields:
        fields = ['open', 'high', 'low', 'close', 'volume']

    from_idx = request.args.get('from_idx', 0)
    size = request.args.get('size', 10)

    result = esapi.es_get_kdata(security_item=securityid, the_date=the_date, start_date=start_date,
                                end_date=end_date, fields=fields, csv=True,
                                level=level, from_idx=int(from_idx), size=int(size))

    return success(result)
