import datetime
import json
from subprocess import Popen, PIPE, CalledProcessError

from kafka import KafkaConsumer
from kafka import KafkaProducer

from fooltrader.api.hq import get_security_list
from fooltrader.contract.kafka_contract import get_kafka_tick_topic, get_kafka_kdata_topic
from fooltrader.settings import KAFKA_HOST, TIME_FORMAT_SEC, TIME_FORMAT_DAY, KAFKA_PATH, ZK_KAFKA_HOST
from fooltrader.utils.utils import get_tick_items, get_kdata_items

producer = KafkaProducer(bootstrap_servers=KAFKA_HOST)


def tick_to_kafka():
    for security_item in get_security_list():
        for tick_items in get_tick_items(security_item):
            for tick_item in tick_items:
                producer.send(get_kafka_tick_topic(security_item['id']),
                              bytes(json.dumps(tick_item, ensure_ascii=False), encoding='utf8'),
                              timestamp_ms=int(datetime.datetime.strptime(tick_item['timestamp'],
                                                                          TIME_FORMAT_SEC).timestamp()))


def kdata_to_kafka(houfuquan):
    for security_item in get_security_list():
        for kdata_item in get_kdata_items(security_item, houfuquan):
            producer.send(get_kafka_kdata_topic(security_item['id'], houfuquan),
                          bytes(json.dumps(kdata_item, ensure_ascii=False), encoding='utf8'),
                          timestamp_ms=int(datetime.datetime.strptime(kdata_item['timestamp'],
                                                                      TIME_FORMAT_DAY).timestamp()))


# make sure delete.topic.enable = true
def delete_topic(topic):
    cmd = '{}/bin/kafka-topics.sh --zookeeper {} --delete --topic {}'.format(KAFKA_PATH, ZK_KAFKA_HOST, topic).split()
    with Popen(cmd, stdout=PIPE, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            print(line, end='')  # process line here

    if p.returncode != 0:
        raise CalledProcessError(p.returncode, p.args)


def list_topics():
    try:
        consumer = KafkaConsumer(bootstrap_servers=[KAFKA_HOST])
        return consumer.topics()
    finally:
        consumer.close()


def delete_all_topics():
    for topic in list_topics():
        delete_topic(topic)


# consume_topic('stock_sh_600000_day_kdata')
kdata_to_kafka(True)
