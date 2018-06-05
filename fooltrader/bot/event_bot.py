# -*- coding: utf-8 -*-

import json
from datetime import datetime, timedelta

import pandas as pd
from kafka import KafkaConsumer
from kafka import TopicPartition

from fooltrader.api.quote import to_security_item
from fooltrader.bot.base_bot import BaseBot
from fooltrader.contract.kafka_contract import get_kafka_tick_topic, get_kafka_kdata_topic
from fooltrader.settings import KAFKA_HOST, TIME_FORMAT_DAY


class EventBot(BaseBot):
    topic = None
    time_step = timedelta(days=1)

    def on_event(self, event_item):
        self.logger.info("got event:{}".format(event_item))

    def dispatch_event(self, topic):
        consumer = KafkaConsumer(topic,
                                 client_id='fooltrader',
                                 group_id=self.bot_name,
                                 value_deserializer=lambda m: json.loads(m.decode('utf8')),
                                 bootstrap_servers=[KAFKA_HOST])
        topic_partition = TopicPartition(topic=topic, partition=0)
        start_timestamp = int(self.start_date.timestamp())

        # 找到以start_timestamp为起点的offset
        partition_map_offset_and_timestamp = consumer.offsets_for_times({topic_partition: start_timestamp})

        if partition_map_offset_and_timestamp:
            offset_and_timestamp = partition_map_offset_and_timestamp[topic_partition]

            if offset_and_timestamp:
                # partition  assigned after poll, and we could seek
                consumer.poll(5, 1)
                # move to the offset
                consumer.seek(topic_partition, offset_and_timestamp.offset)
                # 目前的最大offset
                end_offset = consumer.end_offsets([topic_partition])[topic_partition]
                for message in consumer:
                    message_time = pd.Timestamp(message.value['timestamp'])
                    # 设定了结束日期的话,时间到了或者kafka没数据了就结束
                    if self.end_date and (message_time > self.end_date or message.offset + 1 == end_offset):
                        consumer.close()
                        break

                    self.current_time = message.value['timestamp']

                    self.on_event(message.value)

                    if self.time_step == timedelta(days=1):
                        self.calculate_closing_account()

            else:
                consumer.poll(5, 1)
                consumer.seek(topic_partition, consumer.end_offsets([topic_partition])[topic_partition] - 1)
                message = consumer.poll(5000, 1)
                kafka_end_date = datetime.fromtimestamp(message[topic_partition][0].timestamp).strftime(
                    TIME_FORMAT_DAY)
                self.logger.warn("start:{} is after the last record:{}".format(self.start_date, kafka_end_date))

    def run(self):
        self.logger.info("bot:{} start,account:{}".format(self.bot_name, self.account))

        self.dispatch_event(self.topic)

        self.logger.info("bot:{} end,account:{}".format(self.bot_name, self.account))


class QuoteEventBot(EventBot):
    security_item = None
    event_type = 'quote_day_k'

    def _after_init(self):
        super()._after_init()

        self.security_item = to_security_item(self.security_item)

        if self.security_item is None:
            raise Exception("you must set one security item!")

        if self.event_type == 'quote_day_k':
            self.topic = get_kafka_kdata_topic(security_id=self.security_item['id'])
        elif self.event_type == 'quote_tick':
            self.topic = get_kafka_tick_topic(security_id=self.security_item['id'])
