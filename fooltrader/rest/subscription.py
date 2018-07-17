# -*- coding: utf-8 -*-
import json
import logging

import pandas as pd
from flask import request, Blueprint
from marshmallow import ValidationError

from fooltrader import kafka_producer
from fooltrader.domain.business.es_subscription import PriceSubscription
from fooltrader.domain.business.subscription_schema import PriceSubscriptionSchema
from fooltrader.rest.common import error, success
from fooltrader.utils.utils import fill_doc_type

logger = logging.getLogger(__name__)

ERROR_SUBSCRIPTION_NOT_FOUND = {"code": 200001, "msg": "subscription id:{0} not found"}

ERROR_NO_INPUT_JSON_PROVIDED = {"code": 100001, "msg": "no input json provided"}
ERROR_INVALID_INPUT_JSON = {"code": 100002, "msg": "invalid input json,{0}"}

price_subscription_shema = PriceSubscriptionSchema()

subscription_rest = Blueprint('subscription', __name__,
                              template_folder='templates')


@subscription_rest.route('/subscription', methods=['GET'])
def get_subscription():
    user_id = request.args.get('userId')

    s = PriceSubscription.search()
    s = s.filter('term', userId=user_id)

    results = s.execute()

    return success(results['hits'].to_dict())


@subscription_rest.route('/subscription', defaults={'id': None}, methods=['PUT'])
@subscription_rest.route('/subscription/<id>', methods=['PUT'])
def set_subscription(id):
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
        # FIXME:just check whether exist?
        sub_model = PriceSubscription.get(id=id, ignore=404)
        if not sub_model:
            logger.warning('could not find subscription:{}'.format(id))
            return error(ERROR_SUBSCRIPTION_NOT_FOUND, id)
    else:
        sub_model = PriceSubscription()

    fill_doc_type(sub_model, the_json)

    sub_model.save(force=True)

    result_json = sub_model.to_dict(include_meta=True)

    logger.info('subscription:{} saved'.format(result_json))

    resp = kafka_producer.send('subscription',
                               bytes(json.dumps(result_json), encoding='utf8'),
                               key=bytes(result_json['_id'], encoding='utf8'),
                               timestamp_ms=int(pd.Timestamp.now().timestamp()))
    kafka_producer.flush()

    logger.info(resp)

    return success(payload=result_json)
