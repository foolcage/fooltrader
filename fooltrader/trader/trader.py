import json
import logging
import time
from datetime import datetime, timedelta

from kafka import KafkaConsumer
from kafka import TopicPartition

from fooltrader.contract.kafka_contract import get_kafka_tick_topic, get_kafka_kdata_topic
from fooltrader.domain.Account import Account
from fooltrader.settings import KAFKA_HOST, TIME_FORMAT_DAY

logger = logging.getLogger(__name__)


class Trader(object):
    def __init__(self):
        self.account = Account()

        self.baseCapital = 1000000;
        self.buyCost = 0.001;
        self.sellCost = 0.001;
        self.slippage = 0.001;

        self.start_date = '2013-01-01'
        # listen for ever if not set
        self.end_date = datetime.now().strftime(TIME_FORMAT_DAY)

        self.universe = ('stock_sh_600000', 'stock_sh_600004')

        self.trader_id = 'fool1'

        self.event_time = datetime.strptime(self.start_date, '%Y-%m-%d')
        self.step = timedelta(days=1)

    def buy(self, security_id, amount, current_price=0, order_price=0):
        # 市价交易
        # if order_price == 0:
        #     order = Order()
        #     order.save()
        logger.info("{} buy {} {} with price {}".format(self.trader_id, security_id, amount, current_price))

    def move_on(self, step):
        # 对于回测来说,时间只是加一下
        if self.event_time.date() < datetime.today().date():
            self.event_time += step
        else:
            time.sleep(self.step.total_seconds())

    def on_time_elapsed(self):
        logger.info('event_time:{}'.format(self.event_time))
        self.move_on(self.step)

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
                                break;
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
        while True:
            self.on_time_elapsed()
        for security_id in self.universe:
            if 'on_tick' in dir(self):
                topic = get_kafka_tick_topic(security_id)
                self.__consume_topic_with_func(topic, 'on_tick')
            for level in ('month', 'week', 'day', 'hour', '60', '30', '15', '5', '1'):
                the_func = 'on_{}_bar'.format(level)
                topic = get_kafka_kdata_topic(security_id, True, level)
                self.__consume_topic_with_func(topic, the_func)


if __name__ == '__main__':
    trader = Trader()
    trader.run()
