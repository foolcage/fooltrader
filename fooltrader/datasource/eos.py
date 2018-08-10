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
    if item.get('receiver'):
        receiver = item['receiver']
    else:
        receiver = item['operator']

    return {
        'timestamp': to_time_str(item['block_time'], time_fmt=TIME_FORMAT_MICRO),
        'securityId': 'cryptocurrency_contract_RAM-EOS',
        'code': 'RAM-EOS',
        'price': item['bytes'] / item['price'],
        'direction': direction,
        'volume': item['bytes'],
        'turnover': item['price'],

        'order': item['global_seq'],
        'blockNumber': item['block_num'],
        'action': item['action'],
        'receiver': receiver,
        'trxId': item['trx_id'],
        'operator': item['operator'],
        'fee': item['fee']

    }


def eos_ram_to_kafka():
    ram_trade = db.ram_trade

    logger.info("collection:{}".format(ram_trade))

    earliest_record = ram_trade.find_one({"$query": {}, "$orderby": {"global_seq": 1}})
    latest_record = ram_trade.find_one({"$query": {}, "$orderby": {"global_seq": -1}})

    logger.info("earliest_record:{},latest_record:{}".format(earliest_record, latest_record))

    security_id = 'cryptocurrency_contract_RAM-EOS'

    latest_timestamp, latest_order = get_latest_timestamp_order(security_id)

    topic = get_kafka_tick_topic(security_id)

    if not latest_timestamp:
        latest_timestamp = earliest_record['block_time']

    start_date, end_date = evaluate_time_range(latest_timestamp)

    while True:
        if latest_order and start_date and end_date:
            condition = {"block_time": {"$gte": start_date, "$lt": end_date},
                         "global_seq": {"$gt": latest_order}}
        elif start_date and end_date:
            condition = {"block_time": {"$gte": start_date, "$lt": end_date}}
        elif latest_order:
            condition = {"global_seq": {"$gt": latest_order}}

        logger.info("start_date:{},end_date:{},order:{}".format(start_date, end_date, latest_order))

        latest_timestamp = end_date

        for item in ram_trade.find(condition):
            tick = to_tick(item)

            record_meta = producer.send(topic,
                                        bytes(json.dumps(tick, ensure_ascii=False), encoding='utf8'),
                                        key=bytes(security_id, encoding='utf8'),
                                        timestamp_ms=int(item['block_time'].timestamp() * 1000))
            record = record_meta.get(10)

            latest_timestamp = to_timestamp(record.timestamp)

            latest_order = tick['order']

            logger.debug("tick_to_kafka {}".format(tick))

        if datetime.now() - latest_timestamp < timedelta(minutes=5):
            time.sleep(2)
            logger.info("record latest_timestamp:{},now is:{}".format(latest_timestamp, datetime.now()))
            start_date = None
            end_date = None
        else:
            start_date, end_date = evaluate_time_range(latest_timestamp)


def evaluate_time_range(timestamp, time_step=10):
    start_date = timestamp

    end_date = start_date + timedelta(minutes=time_step)

    return start_date, end_date


if __name__ == '__main__':
    eos_ram_to_kafka()
