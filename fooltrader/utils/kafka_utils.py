# -*- coding: utf-8 -*-
import json
import logging

from kafka import KafkaConsumer, TopicPartition

from fooltrader import KAFKA_HOST
from fooltrader.contract.kafka_contract import get_kafka_tick_topic
from fooltrader.utils.utils import to_timestamp

logger = logging.getLogger(__name__)


def get_latest_timestamp_order_from_topic(topic):
    consumer = KafkaConsumer(topic,
                             # client_id='fooltrader',
                             # group_id='fooltrader',
                             value_deserializer=lambda m: json.loads(m.decode('utf8')),
                             bootstrap_servers=[KAFKA_HOST])
    topic_partition = TopicPartition(topic=topic, partition=0)
    end_offset = consumer.end_offsets([topic_partition])[topic_partition]
    if end_offset > 0:
        # partition  assigned after poll, and we could seek
        consumer.poll(5, 1)

        consumer.seek(topic_partition, end_offset - 1)
        message = consumer.poll(10000, 500)
        msgs = message[topic_partition]
        if len(msgs) > 0:
            record = msgs[-1]
            timestamp = to_timestamp(record.value['timestamp'])
            order = None
            if 'order' in record.value:
                order = record.value['order']
            return timestamp, order
    return None, None


def get_latest_timestamp_order(security_id):
    topic = get_kafka_tick_topic(security_id)
    return get_latest_timestamp_order_from_topic(topic)


if __name__ == '__main__':
    print(get_latest_timestamp_order('stock_sz_300027'))
