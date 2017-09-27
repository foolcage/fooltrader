import json

from kafka import KafkaProducer

from fooltrader.settings import KAFKA_HOST
from fooltrader.utils.utils import get_security_items, get_tick_items, get_kdata_items

producer = KafkaProducer(bootstrap_servers=KAFKA_HOST)


def tick_to_kafka():
    for security_item in get_security_items():
        for tick_items in get_tick_items(security_item):
            for tick_item in tick_items:
                producer.send(security_item['id'] + '_tick',
                              bytes(json.dumps(tick_item, ensure_ascii=False), encoding='utf8'))


def kdata_to_kafka():
    for security_item in get_security_items():
        for kdata_item in get_kdata_items(security_item):
            producer.send(security_item['id'] + '_day_kdata',
                          bytes(json.dumps(kdata_item, ensure_ascii=False), encoding='utf8'))


# tick_to_kafka()
kdata_to_kafka()
