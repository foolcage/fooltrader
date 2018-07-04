# -*- coding: utf-8 -*-
import json
import logging

import pandas as pd
from flask import request, jsonify
from kafka import KafkaProducer

from fooltrader.domain.subscription import Subscription
from fooltrader.rest import app
from fooltrader.settings import KAFKA_HOST
from fooltrader.utils.utils import fill_doc_type

logger = logging.getLogger(__name__)

producer = KafkaProducer(bootstrap_servers=KAFKA_HOST)

{
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

ERROR_SUBSCRIPTION_NOT_FOUND = {"code": 100001, "msg": "subscription id:{0} not found"}


@app.route('/subscription', methods=['GET'])
def get_subscription():
    user_id = request.args.get('userId')

    s = Subscription.search()
    s = s.filter('term', userId=user_id)

    results = s.execute()

    return response(payload=results['hits'].to_dict())


@app.route('/subscription', defaults={'id': None}, methods=['PUT'])
@app.route('/subscription/<id>', methods=['PUT'])
def set_subscription(id):
    the_json = request.get_json()

    # TODO:check params

    if id:
        sub = Subscription.get(id=id, ignore=404)
        if not sub:
            logger.warning('could not find subscription:{}'.format(id))
            return response(id, err=ERROR_SUBSCRIPTION_NOT_FOUND)

    else:
        sub = Subscription()

    fill_doc_type(sub, the_json)

    sub.save(force=True)
    result_json = sub.to_dict(include_meta=True)

    logger.info('subscription:{} saved'.format(result_json))

    resp = producer.send('subscription',
                         bytes(json.dumps(result_json), encoding='utf8'),
                         key=bytes(result_json['_id'], encoding='utf8'),
                         timestamp_ms=int(pd.Timestamp.now().timestamp()))
    producer.flush()
    logger.info(resp)
    return response(payload=result_json)


def response(*msg_args, err=None, code=0, msg='success', payload=None):
    if err:
        if msg_args:
            return jsonify({"code": err['code'], "msg": err['msg'].format(*msg_args)})
        else:
            return jsonify({"code": err['code'], "msg": err['msg']})

    return jsonify({"code": code,
                    "msg": msg,
                    "payload": payload
                    })
