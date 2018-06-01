# -*- coding: utf-8 -*-

import json
import logging
import uuid
from datetime import datetime, timedelta

import pandas as pd
from kafka import KafkaConsumer
from kafka import TopicPartition

from fooltrader.api.quote import to_security_item
from fooltrader.contract.kafka_contract import get_kafka_tick_topic, get_kafka_kdata_topic
from fooltrader.settings import KAFKA_HOST, TIME_FORMAT_DAY
from fooltrader.trader.account import Order, AccountService


class SoloBot(object):
    def on_init(self):
        pass

    def _after_init(self):
        if self.target:
            self.security_item = to_security_item(self.target)

            if self.security_item.empty:
                self.logger.error("could not find {}".format(self.target))

        if type(self.start_date) == str:
            self.start_date = pd.Timestamp(self.start_date)
        if type(self.end_date) == str:
            self.end_date = pd.Timestamp(self.end_date)

        # 时间点
        self.current_time = pd.Timestamp(self.start_date)
        self.account_service = AccountService(self.bot_id,
                                              self.current_time,
                                              base_capital=self.base_capital,
                                              slippage=self.slippage,
                                              buy_cost=self.buy_cost,
                                              sell_cost=self.sell_cost,
                                              stock_fuquan=self.stock_fuquan)

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        self.base_capital = 1000000;
        self.buy_cost = 0.001;
        self.sell_cost = 0.001;
        self.slippage = 0.001;

        # 回测的开始日期
        self.start_date = pd.Timestamp('2013-01-01')
        # 回测的结束日期,为None的话会一直运行
        self.end_date = pd.Timestamp.today()

        # 必须指定且只能指定一个投资标的
        self.target = None

        # 时间步长,用来控制操作的级别
        self.step = timedelta(days=1)

        # 最好自己指定bot_id,方便查看策略表现
        self.bot_id = "{}_{}".format(type(self).__name__.lower(), uuid.uuid4())
        # self.bot_id = type(self).__name__.lower()

        # 如果想以一直运行的方式运行,建议使用hfq(后复权)
        # 只是单纯回测,可以使用qfq(前复权)
        self.stock_fuquan = 'hfq'

        self.on_init()

        self._after_init()

    def buy(self, security_id, current_price, amount=0, pct=1.0, order_price=0):
        self.order(security_id, current_price, amount, pct, order_price, direction=1)

    def sell(self, security_id, current_price, amount=0, pct=1.0, order_price=0):
        self.order(security_id, current_price, amount, pct, order_price, direction=-1)

    # 本质上,订单导致账户(持仓和现金)的变化,价格变化导致账户(市值)的变化
    # 对于T+1来说,日内市值变化意义不大,只需要收盘计算市值即可;
    # 操作(订单)需要用到的是持仓和现金,因此操作(订单)的前后必须同步账户
    # 对于T+0来说,可选按step来计算市值
    def order(self, security_id, current_price, amount=0, pct=1.0, order_price=0, direction=1):
        try:
            # 市价交易
            if order_price == 0:
                order = Order()
                order.botName = self.bot_id
                order.amount = amount
                order.direction = direction
                order.type = 0
                order.price = current_price
                # 买
                if direction == 1:
                    self.account_service.update_position(security_id, amount, pct, current_price, self.current_time)
                elif direction == -1:
                    self.account_service.update_position(security_id, -amount, -pct, current_price, self.current_time)

                order.status = "deal"
                order.timestamp = self.current_time
                # order.save()
                self.logger.info(
                    "{} {} {} {} with price {} success".format(self.bot_id, direction, amount, security_id,
                                                               current_price))
        except Exception as e:
            self.logger.info(
                "{} {} {} {} with price {} failed".format(self.bot_id, direction, amount, security_id,
                                                          current_price))
            self.logger.error(e)

    # def on_tick(self, tick_item):
    #     self.logger.info('on_tick:{}'.format(tick_item))

    def on_day_bar(self, bar_item):
        self.logger.info('on_day_bar:{}'.format(bar_item))

    def __consume_topic_with_func(self, topic, handle_func):
        consumer = KafkaConsumer(topic,
                                 client_id='fooltrader',
                                 group_id=self.bot_id,
                                 value_deserializer=lambda m: json.loads(m.decode('utf8')),
                                 bootstrap_servers=[KAFKA_HOST])
        topic_partition = TopicPartition(topic=topic, partition=0)
        start_timestamp = int(self.start_date.timestamp())

        partition_map_offset_and_timestamp = consumer.offsets_for_times({topic_partition: start_timestamp})

        if partition_map_offset_and_timestamp:
            offset_and_timestamp = partition_map_offset_and_timestamp[topic_partition]

            if offset_and_timestamp:
                # partition  assigned after poll, and we could seek
                consumer.poll(5, 1)
                consumer.seek(topic_partition, offset_and_timestamp.offset)
                end_offset = consumer.end_offsets([topic_partition])[topic_partition]
                for message in consumer:
                    message_time = pd.Timestamp(message.value['timestamp'])
                    # 设定了结束日期的话,时间到了或者kafka没数据了就结束
                    if self.end_date and (message_time > self.end_date or message.offset + 1 == end_offset):
                        consumer.close()
                        break

                    getattr(self, handle_func)(message.value)


            else:
                consumer.poll(5, 1)
                consumer.seek(topic_partition, consumer.end_offsets([topic_partition])[topic_partition] - 1)
                message = consumer.poll(5000, 1)
                kafka_start_date = datetime.fromtimestamp(message[topic_partition][0].timestamp).strftime(
                    TIME_FORMAT_DAY)
                self.logger.warn("start:{} is after the last record:{}".format(self.start_date, kafka_start_date))

    def run(self):
        if self.target and not self.security_item.empty:
            if 'on_tick' in dir(self) and 'on_day_bar' in dir(self):
                self.logger.error("on_tick or on_day_bar,but not both")
            else:
                if 'on_tick' in dir(self):
                    handle_func = 'on_tick'
                elif 'on_day_bar' in dir(self):
                    handle_func = 'on_day_bar'

                consumer = KafkaConsumer(bootstrap_servers=[KAFKA_HOST])
                current_topics = consumer.topics()

                if handle_func == 'on_tick':
                    topic = get_kafka_tick_topic(self.security_item['id'])
                elif handle_func == 'on_day_bar':
                    topic = get_kafka_kdata_topic(self.security_item['id'], fuquan=self.stock_fuquan)

                if topic in current_topics:
                    self.__consume_topic_with_func(topic, handle_func)
                else:
                    self.logger.error("topic:{} not in kafka".format(topic))

        else:
            self.logger.error("you must set a target for investing.")


if __name__ == '__main__':
    from elasticsearch_dsl.connections import connections

    connections.create_connection(hosts=['localhost'], timeout=20)

    trader = SoloBot()
    trader.run()
