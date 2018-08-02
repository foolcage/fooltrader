# -*- coding: utf-8 -*-
import json
import logging
import time
from datetime import timedelta, datetime

from kafka import KafkaProducer
from pymongo import MongoClient

from fooltrader import to_time_str
from fooltrader.contract.kafka_contract import get_kafka_tick_topic
from fooltrader.settings import EOS_MONGODB_URL, KAFKA_HOST, TIME_FORMAT_MICRO
from fooltrader.utils.kafka_utils import get_latest_timestamp_order
from fooltrader.utils.utils import to_timestamp

logger = logging.getLogger(__name__)

producer = KafkaProducer(bootstrap_servers=KAFKA_HOST)

client = MongoClient(EOS_MONGODB_URL)

db = client['eosMain']


def to_tick(item):
    if item['action'] == 'buyrambytes' or item['action'] == 'buyram':
        direction = 1
    elif item['action'] == 'sellram':
        direction = -1
    else:
        direction = 0

    return {
        'timestamp': to_time_str(item['block_time'], time_fmt=TIME_FORMAT_MICRO),
        'securityId': 'cryptocurrency_contact_RAM-EOS',
        'code': 'RAM-EOS',
        'price': item['bytes'] / item['price'],
        'direction': direction,
        'volume': item['bytes'],
        'turnover': item['price'],

        'order': item['global_seq'],
        'blockNumber': item['block_num'],
        'action': item['action'],
        'receiver': item['receiver'],
        'trxId': item['trx_id'],
        'operator': item['operator'],
        'fee': item['fee']

    }


def eos_ram_to_kafka():
    security_id = 'cryptocurrency_contact_RAM-EOS'

    latest_timestamp, latest_order = get_latest_timestamp_order(security_id)

    topic = get_kafka_tick_topic(security_id)

    if not latest_timestamp:
        latest_timestamp = to_timestamp('2018-06-09')

    start_date, end_date = evaluate_time_range(latest_timestamp)

    while True:
        if latest_order:
            condition = {"block_time": {"$gte": start_date, "$lt": end_date},
                         "global_seq": {"$gt": latest_order}}
        else:
            condition = {"block_time": {"$gte": start_date, "$lt": end_date}}

        for item in db.ram_trade.find(condition):
            tick = to_tick(item)

            record_meta = producer.send(topic,
                                        bytes(json.dumps(tick, ensure_ascii=False), encoding='utf8'),
                                        key=bytes(security_id, encoding='utf8'),
                                        timestamp_ms=int(item['block_time'].timestamp() * 1000))
            record = record_meta.get(10)

            latest_timestamp = to_timestamp(record.timestamp)

            latest_order = tick['order']

            logger.debug("tick_to_kafka {}".format(tick))

        if datetime.now() - latest_timestamp < timedelta(seconds=2):
            time.sleep(1)

        start_date, end_date = evaluate_time_range(latest_timestamp)


def evaluate_time_range(timestamp):
    start_date = timestamp

    end_date = start_date + timedelta(minutes=10)

    return start_date, end_date


if __name__ == '__main__':
    eos_ram_to_kafka()
