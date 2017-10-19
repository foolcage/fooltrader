import json
import logging
from datetime import datetime

from kafka import KafkaConsumer
from kafka import TopicPartition

from fooltrader.domain.Account import Account, Order
from fooltrader.settings import KAFKA_HOST, TIME_FORMAT_DAY
from fooltrader.utils.data_contract import get_kafka_tick_topic, get_kafka_kdata_topic

logger = logging.getLogger(__name__)


class Trader(object):
    account = Account()

    baseCapital = 1000000;
    buyCost = 0.001;
    sellCost = 0.001;
    slippage = 0.001;

    start_date = '2015-1-1'
    # listen for ever if not set
    end_date = datetime.now().strftime(TIME_FORMAT_DAY)

    universe = ('stock_sh_600000', 'stock_sh_600004')

    trader_id = 'fool1'

    def buy(self, security_id, amount, current_price=0, order_price=0):
        # 市价交易
        if order_price == 0:
            order = Order()
            order.save()

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
        for security_id in self.universe:
            if 'on_tick' in dir(self):
                topic = get_kafka_tick_topic(security_id)
                self.__consume_topic_with_func(topic, 'on_tick')
            for level in ('month', 'week', 'day', 'hour', '60', '30', '15', '5', '1'):
                the_func = 'on_{}_bar'.format(level)
                topic = get_kafka_kdata_topic(security_id, True, level)
                self.__consume_topic_with_func(topic, the_func)


trader = Trader()
trader.run()
