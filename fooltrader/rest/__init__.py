# -*- coding: utf-8 -*-
from flask import Flask, Config

from fooltrader import FOOLTRADER_STORE_PATH
from fooltrader.domain.business.es_subscription import PriceSubscription, SubscriptionTriggered
from fooltrader.rest.security import security_rest
from fooltrader.rest.subscription import subscription_rest
from fooltrader.utils.es_utils import es_index_mapping

es_index_mapping('price_subscription', PriceSubscription)
es_index_mapping('subscription_triggered', SubscriptionTriggered)

app = Flask(__name__)

app.debug = True

app.config.from_object(Config(root_path=FOOLTRADER_STORE_PATH))

app.register_blueprint(security_rest)
app.register_blueprint(subscription_rest)
