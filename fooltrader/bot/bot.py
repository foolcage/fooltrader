# -*- coding: utf-8 -*-
import datetime
import json
import logging
import threading

from kafka import KafkaConsumer
from kafka import TopicPartition

from fooltrader.api.technical import to_security_item
from fooltrader.bot.action.account_action import AccountService
from fooltrader.bot.action.msg_action import WeixinAction, EmailAction
from fooltrader.contract.kafka_contract import get_kafka_tick_topic
from fooltrader.settings import KAFKA_HOST
from fooltrader.utils.kafka_utils import get_latest_timestamp_order_from_topic
from fooltrader.utils.utils import to_timestamp


class BaseBot(object):
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.bot_name = type(self).__name__.lower()


class EventBot(BaseBot):
    func_map_topic = {'on_subscription': 'subscription'}

    def on_init(self):
        pass

    def on_event(self, event_item):
        self.logger.info("got event:{}".format(event_item))

    def __init__(self, security_id=None):
        super().__init__()
        self.security_id = security_id
        self.start_timestamp = None
        self.end_timestamp = None

        # setup the user custom settings
        self.on_init()

        assert self.security_id is not None

        self.security_item = to_security_item(self.security_id)
        assert self.security_item is not None

        self._threads = []

        self.quote_topic = get_kafka_tick_topic(security_id=self.security_id)

        self.logger.info(
            "bot:{} listen to security:{} topic:{}".format(self.bot_name, self.security_id, self.quote_topic))

    def __repr__(self):
        return '{}({})'.format(
            self.__class__.__name__,
            ', '.join("{}={}".format(key, self.__dict__[key]) for key in self.__dict__ if key != 'logger'))

    def consume_topic_with_func(self, topic, func):
        consumer = KafkaConsumer(topic,
                                 client_id='fooltrader',
                                 group_id=self.bot_name,
                                 value_deserializer=lambda m: json.loads(m.decode('utf8')),
                                 bootstrap_servers=[KAFKA_HOST])
        topic_partition = TopicPartition(topic=topic, partition=0)

        if self.start_timestamp:
            start_timestamp = int(self.start_timestamp.timestamp() * 1000)

            end_offset = consumer.end_offsets([topic_partition])[topic_partition]
            if end_offset == 0:
                self.logger.warning("topic:{} end offset:{}".format(topic, end_offset))
                self.logger.error("the topic:{} has no data,but you want to backtest".format(self.quote_topic))
                return

            # find the offset from start_timestamp
            offset_and_timestamp = consumer.offsets_for_times({topic_partition: start_timestamp})

            if offset_and_timestamp:
                offset_and_timestamp = offset_and_timestamp[topic_partition]

                if offset_and_timestamp:
                    # partition  assigned after poll, and we could seek
                    consumer.poll(5, 1)
                    # move to the offset
                    consumer.seek(topic_partition, offset_and_timestamp.offset)

                    for message in consumer:
                        if 'timestamp' in message.value:
                            message_time = to_timestamp(message.value['timestamp'])
                        else:
                            message_time = to_timestamp(message.timestamp)

                        if self.end_timestamp and (message_time > self.end_timestamp):
                            consumer.close()
                            break

                        getattr(self, func)(message.value)

                else:
                    latest_timestamp, _ = get_latest_timestamp_order_from_topic(self.quote_topic)
                    self.logger.warning(
                        "start:{} is after the last record:{}".format(self.start_timestamp, latest_timestamp))

    def run(self):
        self.logger.info("start bot:{}".format(self))

        funcs = set(dir(self)) & self.func_map_topic.keys()

        consumer = KafkaConsumer(bootstrap_servers=[KAFKA_HOST])
        current_topics = consumer.topics()

        for func in funcs:
            topic = self.func_map_topic.get(func)
            if topic not in current_topics:
                self.logger.exception("you implement func:{},but the topic:{} for it not exist".format(func, topic))
                continue

            self._threads.append(
                threading.Thread(target=self.consume_topic_with_func, args=(self.func_map_topic.get(func), func)))

        for the_thread in self._threads:
            the_thread.start()

        self.consume_topic_with_func(self.quote_topic, 'on_event')

        self.logger.info("finish bot:{}".format(self))


class TradingEventBot(EventBot):
    def after_init(self):
        pass

    def __init__(self, security_id=None):
        self.base_capital = 1000000
        self.buy_cost = 0.001
        self.sell_cost = 0.001
        self.slippage = 0.001

        super().__init__(security_id)

        timestamp = self.start_timestamp
        if not timestamp:
            timestamp = datetime.datetime.now()
        self.account_service = AccountService(bot_name=self.bot_name, timestamp=timestamp,
                                              base_capital=self.base_capital, buy_cost=self.buy_cost,
                                              sell_cost=self.sell_cost, slippage=self.slippage)

        self.after_init()


class NotifyEventBot(EventBot):
    def after_init(self):
        pass

    def __init__(self, security_id=None):
        self.notify_weixin = False
        self.notify_email = False

        super().__init__(security_id)

        if self.notify_weixin:
            self.weixin_action = WeixinAction()
        if self.notify_email:
            self.email_action = EmailAction()

        self.after_init()
