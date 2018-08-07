# -*- coding: utf-8 -*-

import json
import logging
import uuid
from datetime import datetime, timedelta

import pandas as pd
from kafka import TopicPartition

from fooltrader.api.technical import to_security_item
from fooltrader.settings import KAFKA_HOST, TIME_FORMAT_DAY


class SoloBot(object):
    pass
