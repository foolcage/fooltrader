# -*- coding: utf-8 -*-

import json
import logging
import time
from datetime import datetime, timedelta

import pandas as pd
from kafka import KafkaConsumer
from kafka import TopicPartition

from fooltrader.api.quote import to_security_item
from fooltrader.bot.account_service import AccountService
from fooltrader.contract.kafka_contract import get_kafka_tick_topic, get_kafka_kdata_topic
from fooltrader.settings import KAFKA_HOST, TIME_FORMAT_DAY

EVENT_MARKET_OPEN = 0
EVENT_MARKET_CLOSE = 1


class BaseBot(object):
    def on_init(self):
        pass

    def on_event(self, event_item):
        self.logger.info("got event:{}".format(event_item))

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        self.on_init()

        # 回测的开始日期
        if not hasattr(self, 'start_date'):
            self.start_date = pd.Timestamp('2013-01-01')
        # 回测的结束日期,为None的话会一直运行
        if not hasattr(self, 'end_date'):
            self.end_date = pd.Timestamp.today()

        # 交易机器人需要账户，只是做监听告警之类不需要
        if not hasattr(self, 'need_account'):
            self.need_account = True

        if self.need_account:
            if not hasattr(self, 'base_capital'):
                self.base_capital = 1000000

            if not hasattr(self, 'buy_cost'):
                self.buy_cost = 0.001

            if not hasattr(self, 'sell_cost'):
                self.sell_cost = 0.001

            if not hasattr(self, 'slippage'):
                self.slippage = 0.001

            if not hasattr(self, 'stock_fuquan'):
                self.stock_fuquan = 'hfq'

        self.bot_name = type(self).__name__.lower()

        # 指定security_item就监听其某级别的行情，否则为只收到timer信息，需要自己主动去查询行情
        if hasattr(self, 'security_item'):
            if not self.security_item:
                raise Exception("you must set one security item!")

            self.security_item = to_security_item(self.security_item)

            if self.security_item is None:
                raise Exception("invalid security item:{}".format(self.security_item))

            # 默认日级别行情
            if not hasattr(self, 'level'):
                self.level = 'day'

            self.logger.info(
                "bot:{} listen to security_item:{},level:{}".format(self.bot_name, self.security_item, self.level))

            if self.level == 'day':
                self.topic = get_kafka_kdata_topic(security_id=self.security_item['id'], level=self.level)
            elif self.level == 'tick':
                self.topic = get_kafka_tick_topic(security_id=self.security_item['id'])
            else:
                self.logger.error("wrong level:{}".format(self.level))
        else:
            # 默认日级别timer
            if not hasattr(self, 'time_step'):
                self.time_step = timedelta(days=1)
            self.logger.info("bot:{} check the market by itself,time_step:{}".format(self.bot_name, self.time_step))

        self._after_init()

    def _after_init(self):
        if type(self.start_date) == str:
            self.start_date = pd.Timestamp(self.start_date)
        if type(self.end_date) == str:
            self.end_date = pd.Timestamp(self.end_date)

        # 时间点
        self.current_time = pd.Timestamp(self.start_date)

        # 是否需要账户，回测需要，只是监听和告警不需要
        if self.need_account:
            self.account_service = AccountService(bot_name=self.bot_name, timestamp=self.current_time,
                                                  base_capital=self.base_capital, buy_cost=self.buy_cost,
                                                  sell_cost=self.sell_cost, slippage=self.slippage,
                                                  stock_fuquan=self.stock_fuquan)

    def __repr__(self):
        return '{}({})'.format(
            self.__class__.__name__,
            ', '.join("{}={}".format(key, self.__dict__[key]) for key in self.__dict__ if key != 'logger'))

    def dispatch_event(self, topic):
        if not topic:
            while True:
                self.on_event({"timestamp": self.current_time})

                if self.current_time + self.time_step > pd.Timestamp.now():
                    time.sleep(self.time_step.seconds)
                else:
                    self.current_time += self.time_step

        consumer = KafkaConsumer(topic,
                                 # client_id='fooltrader',
                                 # group_id=self.bot_name,
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

                    flag = message.value.get('flag')
                    # 收市计算账户
                    if flag and flag == EVENT_MARKET_CLOSE and self.need_account:
                        self.account_service.calculate_closing_account(self.current_time)

                    self.on_event(message.value)

            else:
                consumer.poll(5, 1)
                consumer.seek(topic_partition, consumer.end_offsets([topic_partition])[topic_partition] - 1)
                message = consumer.poll(5000, 1)
                kafka_end_date = datetime.fromtimestamp(message[topic_partition][0].timestamp).strftime(
                    TIME_FORMAT_DAY)
                self.logger.warning("start:{} is after the last record:{}".format(self.start_date, kafka_end_date))

    def run(self):
        self.logger.info("start bot:{}".format(self))

        self.dispatch_event(self.topic)

        self.logger.info("finish bot:{}".format(self))
