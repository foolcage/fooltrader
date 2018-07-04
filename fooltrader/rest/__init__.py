# -*- coding: utf-8 -*-
from flask import Flask, Config

from fooltrader import FOOLTRADER_STORE_PATH
from fooltrader.domain.subscription import Subscription, SubscriptionTriggered
from fooltrader.utils.es_utils import es_index_mapping

app = Flask(__name__)
app.config.from_object(Config(root_path=FOOLTRADER_STORE_PATH))

es_index_mapping('subscription', Subscription)
es_index_mapping('subscription_triggered', SubscriptionTriggered)
