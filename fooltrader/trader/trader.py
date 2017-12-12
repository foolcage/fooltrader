import json
import logging
import threading
import time
import uuid
from datetime import datetime, timedelta

from kafka import KafkaConsumer
from kafka import TopicPartition

from fooltrader.contract.kafka_contract import get_kafka_tick_topic, get_kafka_kdata_topic
from fooltrader.settings import KAFKA_HOST, TIME_FORMAT_DAY
from fooltrader.trader.account import Order, AccountService

logger = logging.getLogger(__name__)


class Trader(object):
    def __init__(self):
        self.base_capital = 1000000;
        self.buy_cost = 0.001;
        self.sell_cost = 0.001;
        self.slippage = 0.001;

        # 回测的开始日期
        self.start_date = '2013-01-01'
        # 回测的结束日期,为None的话会always running
        self.end_date = datetime.now().strftime(TIME_FORMAT_DAY)

        # 证券标的,可以动态增删,从而动态接收行情
        # 为None的话,可采用poll的方式去查任何标的的行情
        # 当然,两种方式可以同时进行,它们会跑在不同的线程
        self.universe = None

        self.event_time = datetime.strptime(self.start_date, '%Y-%m-%d')
        self.step = timedelta(days=1)

        self.trader_id = "{}_{}".format(type(self).__name__.lower(), uuid.uuid4())

        self.account_service = AccountService(self.trader_id,
                                              self.event_time,
                                              base_capital=self.base_capital,
                                              slippage=self.slippage,
                                              buy_cost=self.buy_cost,
                                              sell_cost=self.sell_cost)

    def buy(self, security_id, current_price, amount=0, pct=1.0, order_price=0):
        self.order(security_id, current_price, amount, pct, order_price, direction=1)

    def sell(self, security_id, current_price, amount=0, pct=1.0, order_price=0):
        self.order(security_id, current_price, amount, pct, order_price, direction=-1)

    def order(self, security_id, current_price, amount=0, pct=1.0, order_price=0, direction=1):
        try:
            # 市价交易
            if order_price == 0:
                order = Order()
                order.traderId = self.trader_id
                order.amount = amount
                order.direction = direction
                order.type = 0
                order.price = current_price
                # 买
                if direction == 1:
                    self.account_service.update_position(security_id, amount, pct, current_price, self.event_time)
                elif direction == -1:
                    self.account_service.update_position(security_id, -amount, -pct, current_price, self.event_time)

                order.status = "deal"
                order.timestamp = self.event_time
                # order.save()
                logger.info(
                    "{} {} {} {} with price {} success".format(self.trader_id, direction, amount, security_id,
                                                               current_price))
        except Exception as e:
            logger.info(
                "{} {} {} {} with price {} failed".format(self.trader_id, direction, amount, security_id,
                                                          current_price))
            logger.error(e)

    def move_on(self, step):
        # 对于回测来说,时间只是加一下
        if self.event_time.date() < datetime.today().date():
            self.event_time += step
        else:
            time.sleep(self.step.total_seconds())

    def on_time_elapsed(self):
        logger.info('event_time:{}'.format(self.event_time))

    def on_tick(self, tick_item):
        logger.info('on_tick:{}'.format(tick_item))

    def on_day_bar(self, bar_item):
        logger.info('on_day_bar:{}'.format(bar_item))

    def __consume_topic_with_func(self, topic, func):
        if func in dir(self):
            consumer = KafkaConsumer(bootstrap_servers=[KAFKA_HOST])
            current_topics = consumer.topics()
            if topic in current_topics:
                consumer = KafkaConsumer(topic,
                                         client_id='fooltrader',
                                         group_id=self.trader_id,
                                         value_deserializer=lambda m: json.loads(m.decode('utf8')),
                                         bootstrap_servers=[KAFKA_HOST])
                topic_partition = TopicPartition(topic=topic, partition=0)
                start_timestamp = int(datetime.strptime(self.start_date, TIME_FORMAT_DAY).timestamp())
                end_timestamp = int(datetime.strptime(self.end_date, TIME_FORMAT_DAY).timestamp())

                partition_map_offset_and_timestamp = consumer.offsets_for_times({topic_partition: start_timestamp})

                if partition_map_offset_and_timestamp:
                    offset_and_timestamp = partition_map_offset_and_timestamp[topic_partition]

                    if offset_and_timestamp:
                        # partition  assigned after poll, and we could seek
                        consumer.poll(5, 1)
                        consumer.seek(topic_partition, offset_and_timestamp.offset)
                        end_offset = consumer.end_offsets([topic_partition])[topic_partition]
                        for message in consumer:
                            if self.end_date and (message.value[
                                                      'timestamp'] > self.end_date or message.offset + 1 == end_offset):
                                consumer.close()
                                break
                            getattr(self, func)(message.value)
                    else:
                        consumer.poll(5, 1)
                        consumer.seek(topic_partition, consumer.end_offsets([topic_partition])[topic_partition] - 1)
                        message = consumer.poll(5000, 1)
                        kafka_start_date = datetime.fromtimestamp(message[topic_partition][0].timestamp).strftime(
                            TIME_FORMAT_DAY)
                        logger.warn("start:{} is after the last record:{}".format(self.start_date, kafka_start_date))
            else:
                logger.error("topic:{} not in kafka".format(topic))

    def run(self):
        if self.universe:
            for security_id in self.universe:
                if 'on_tick' in dir(self):
                    topic = get_kafka_tick_topic(security_id)
                    threading.Thread(target=self.__consume_topic_with_func, args=(topic, 'on_tick')).start()
                for level in ('month', 'week', 'day', 'hour', '60', '30', '15', '5', '1'):
                    the_func = 'on_{}_bar'.format(level)
                    topic = get_kafka_kdata_topic(security_id, True, level)
                    threading.Thread(target=self.__consume_topic_with_func, args=(topic, the_func)).start()
        while True:
            self.on_time_elapsed()
            self.move_on(self.step)
            self.account_service.save(self.event_time)


if __name__ == '__main__':
    trader = Trader()
    trader.run()
