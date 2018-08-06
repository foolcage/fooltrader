# -*- coding: utf-8 -*-
import datetime
import json
import logging
from subprocess import Popen, PIPE, CalledProcessError

from kafka import KafkaConsumer
from kafka import KafkaProducer

from fooltrader.api.technical import get_security_list, get_ticks, get_kdata, to_security_item
from fooltrader.contract.kafka_contract import get_kafka_tick_topic, get_kafka_kdata_topic
from fooltrader.datasource.ccxt_wrapper import fetch_ticks
from fooltrader.settings import KAFKA_HOST, TIME_FORMAT_SEC, TIME_FORMAT_DAY, KAFKA_PATH, ZK_KAFKA_HOST

producer = KafkaProducer(bootstrap_servers=KAFKA_HOST)

logger = logging.getLogger(__name__)


def tick_to_kafka(security_item=None):
    if security_item:
        _tick_to_kafka(security_item)
    else:
        for _, security_item in get_security_list().iterrows():
            _tick_to_kafka(security_item)


def _tick_to_kafka(security_item):
    security_item = to_security_item(security_item)

    for df in get_ticks(security_item):
        for _, tick_item in df.iterrows():
            the_json = tick_item.to_json(force_ascii=False)
            producer.send(get_kafka_tick_topic(security_item['id']),
                          bytes(the_json, encoding='utf8'),
                          timestamp_ms=int(1000 * datetime.datetime.strptime(tick_item['timestamp'],
                                                                             TIME_FORMAT_SEC).timestamp()))
            logger.debug("tick_to_kafka {}".format(the_json))


def kdata_to_kafka(security_item=None, fuquan='hfq'):
    if security_item:
        _kdata_to_kafka(security_item, fuquan)
    else:
        for _, security_item in get_security_list().iterrows():
            _kdata_to_kafka(security_item, fuquan)


def _kdata_to_kafka(security_item, fuquan='hfq'):
    security_item = to_security_item(security_item)

    for _, kdata_item in get_kdata(security_item, fuquan=fuquan).iterrows():
        the_json = kdata_item.to_json(force_ascii=False)
        producer.send(get_kafka_kdata_topic(security_item['id'], fuquan),
                      bytes(the_json, encoding='utf8'),
                      timestamp_ms=int(datetime.datetime.strptime(kdata_item['timestamp'],
                                                                  TIME_FORMAT_DAY).timestamp()))
        logger.debug("kdata_to_kafka {}".format(the_json))


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


def cryptocurrency_tick_to_kafka(exchange, pairs=None):
    for tick in fetch_ticks(exchange, pairs=pairs):
        producer.send(get_kafka_tick_topic(tick['securityId']),
                      bytes(json.dumps(tick), encoding='utf8'),
                      timestamp_ms=tick['timestamp'])

        logger.debug("tick_to_kafka {}".format(tick))


if __name__ == '__main__':
    # kdata_to_kafka(security_item='300027', fuquan='hfq')
    tick_to_kafka(security_item='300027')
    # cryptocurrency_tick_to_kafka('kraken')
    # parser = argparse.ArgumentParser()
    # parser.add_argument('security_type', help='the security type')
    # parser.add_argument('exchange', help='the exchange')
    # parser.add_argument('codes', nargs='+', help='the security code list')
    #
    # args = parser.parse_args()
    #
    # if args.security_type == 'cryptocurrency':
    #     pairs = [code.replace('-', '/') for code in args.codes]
    #
    #     cryptocurrency_tick_to_kafka(exchange=args.exchange, pairs=pairs)
