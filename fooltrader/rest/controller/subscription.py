# -*- coding: utf-8 -*-
import json
import logging
from datetime import datetime

import pandas as pd
from flask import request
from marshmallow import ValidationError

from fooltrader import kafka_producer
from fooltrader.api.esapi import esapi
from fooltrader.domain.business.es_subscription import PriceSubscription, PriceSubscriptionSchema
from fooltrader.rest import app
from fooltrader.rest.common import error, success
from fooltrader.rest.err_codes import ERROR_NO_INPUT_JSON_PROVIDED, ERROR_INVALID_INPUT_JSON, \
    ERROR_SUBSCRIPTION_NOT_FOUND, ERROR_MISSING_REQUEST_PARAMS
from fooltrader.settings import TIME_FORMAT_MICRO
from fooltrader.utils.utils import fill_doc_type, get_security_id, to_time_str

logger = logging.getLogger(__name__)

price_subscription_shema = PriceSubscriptionSchema()


@app.route('/subscription', methods=['GET'])
def get_subscription():
    user_id = request.args.get('userId')

    if not user_id:
        return error(ERROR_MISSING_REQUEST_PARAMS, 'user_id')

    result = esapi.es_get_subscription(user_id)
    return success(result)


@app.route('/subscription/<sub_type>', defaults={'id': None}, methods=['PUT'])
@app.route('/subscription/<sub_type>/<id>', methods=['PUT'])
def set_subscription(sub_type, id):
    the_json = request.get_json()

    if not the_json:
        return error(ERROR_NO_INPUT_JSON_PROVIDED)

    # Validate and deserialize input
    try:
        sub_dict, _ = price_subscription_shema.load(the_json)
    except ValidationError as err:
        return error(ERROR_INVALID_INPUT_JSON, err.messages)

    # the update operation
    if id:
        sub_model = PriceSubscription.get(id=id, ignore=404)
        sub_dict['id'] = id
        if not sub_model:
            logger.warning('could not find subscription:{}'.format(id))
            return error(ERROR_SUBSCRIPTION_NOT_FOUND, id)
    else:
        # generate securityId
        sub_dict['securityId'] = get_security_id(sub_dict['securityType'], sub_dict['exchange'], sub_dict['code'])
        # generate subscription id
        sub_dict['id'] = "{}_{}".format(sub_dict['userId'], sub_dict['securityId'])

        sub_dict['timestamp'] = to_time_str(datetime.now(), time_fmt=TIME_FORMAT_MICRO)

        sub_model = PriceSubscription(meta={'id': sub_dict['id']})

    fill_doc_type(sub_model, sub_dict)

    sub_model.save(force=True)

    result_json = sub_model.to_dict(include_meta=True)

    logger.info('subscription:{} saved'.format(result_json))

    resp = kafka_producer.send('subscription',
                               bytes(json.dumps(sub_dict), encoding='utf8'),
                               key=bytes(sub_dict['id'], encoding='utf8'),
                               timestamp_ms=int(pd.Timestamp.now().timestamp() * 1000))
    kafka_producer.flush()

    logger.info(resp)

    return success(payload=result_json)
