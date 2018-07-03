# -*- coding: utf-8 -*-
import logging

from flask import request, jsonify

from fooltrader.domain.subscription import Subscription
from fooltrader.rest import app
from fooltrader.utils.utils import fill_doc_type

logger = logging.getLogger(__name__)

{
    "id": 123,
    "userId": 111,
    "securityType": "cryptocurrency",
    "exchange": "binance",
    "code": "BTC-USDT",
    "condition": {
        "upPct": 1,
        "downPct": 2,
        "up": 7000,
        "down": 6000,
        "cross": 0.02
    },
    "repeat": False
}


@app.route('/subscription', methods=['GET'])
def get_subscription():
    user_id = request.args.get('userId')

    s = Subscription.search()
    s = s.filter('term', userId=user_id)

    results = s.execute()

    return response(results)


@app.route('/subscription', defaults={'id': None}, methods=['PUT'])
@app.route('/subscription/<id>', methods=['PUT'])
def set_subscription(id):
    the_json = request.get_json()

    # TODO:check params

    if id:
        sub = Subscription.get(id=id, ignore=404)
        if not sub:
            logger.warning('could not find subscription:{}'.format(id))
            return

    else:
        sub = Subscription()

    fill_doc_type(sub, the_json)

    sub.save()

    logger.info('subscription:{} saved'.format(sub))
    return response(sub.to_dict(include_meta=True))


def response(code=0, msg='success', payload=None):
    return jsonify({"code": code,
                    "msg": msg,
                    "payload": payload
                    })
