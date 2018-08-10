# -*- coding: utf-8 -*-
from flask import request

from fooltrader.api.esapi import esapi
from fooltrader.rest import app
from fooltrader.rest.common import success, get_request_params_as_list


@app.route('/tech/kdata/<securityid>', methods=['GET'])
def get_kdata(securityid):
    the_date = request.args.get('the_date')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    level = request.args.get('level', 'day')

    fields = request.args.get('fields')
    if not fields:
        fields = ['timestamp', 'open', 'high', 'low', 'close', 'volume']

    from_idx = request.args.get('from_idx', 0)
    size = request.args.get('size', 500)

    result = esapi.es_get_kdata(security_item=securityid, the_date=the_date, start_date=start_date,
                                end_date=end_date, fields=fields, csv=True,
                                level=level, from_idx=int(from_idx), size=int(size))

    return success(result)


@app.route('/tech/statistic/<securityid>', methods=['GET'])
def get_statistic(securityid):
    the_date = request.args.get('the_date')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    level = request.args.get('level', 'day')

    from_idx = request.args.get('from_idx', 0)
    size = request.args.get('size', 500)

    result = esapi.es_get_statistic(security_item=securityid, the_date=the_date, start_date=start_date,
                                    end_date=end_date, level=level, from_idx=int(from_idx), size=int(size))

    return success(result)


@app.route('/tech/user_statistic/<main_chain>', defaults={'user_id': None}, methods=['GET'])
@app.route('/tech/user_statistic/<main_chain>/<user_id>', methods=['GET'])
def get_user_statistic(main_chain, user_id):
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    security_id = request.args.get('security_id', 'cryptocurrency_contract_RAM-EOS')

    from_idx = request.args.get('from_idx', 0)
    size = request.args.get('size', 100)

    result = esapi.es_get_user_statistic(main_chain=main_chain, security_id=security_id, user_id=user_id,
                                         start_date=start_date,
                                         end_date=end_date, from_idx=int(from_idx), size=int(size))

    return success(result)


@app.route('/tech/account/<main_chain>', defaults={'user_id': None}, methods=['GET'])
@app.route('/tech/account/<main_chain>/<user_id>', methods=['GET'])
def get_accounts(main_chain, user_id):
    start_vol = request.args.get('start_vol')
    end_vol = request.args.get('end_vol')

    from_idx = request.args.get('from_idx', 0)
    size = request.args.get('size', 100)
    order = request.args.get('order', 'totalEos')

    fields = get_request_params_as_list(request, 'fields')

    result = esapi.es_get_accounts(main_chain=main_chain, user_id=user_id,
                                   start_vol=int(start_vol), fields=fields,
                                   end_vol=int(end_vol), from_idx=int(from_idx), size=int(size), order=order)

    return success(result)
