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

        # 时间点
        self.current_time = datetime.strptime(self.start_date, '%Y-%m-%d')
        # 时间步长,用来控制操作的级别
        self.step = timedelta(days=1)

        self.trader_id = "{}_{}".format(type(self).__name__.lower(), uuid.uuid4())

        # 如果想以always running的方式运行,建议使用hfq(后复权)
        # 只是单纯回测,可以使用qfq(前复权)
        self.stock_fuquan = 'hfq'

        self.account_service = AccountService(self.trader_id,
                                              self.current_time,
                                              base_capital=self.base_capital,
                                              slippage=self.slippage,
                                              buy_cost=self.buy_cost,
                                              sell_cost=self.sell_cost,
                                              stock_fuquan=self.stock_fuquan)
        # 最小级别
        self.min_level = 'on_day'

        self.level_consuming_time = {}

        self.level_step = {'on_tick': timedelta(seconds=3),
                           'on_1_bar': timedelta(minutes=1),
                           'on_5_bar': timedelta(minutes=5),
                           'on_15_bar': timedelta(minutes=15),
                           'on_30_bar': timedelta(minutes=30),
                           'on_60_bar': timedelta(minutes=60),
                           'on_day_bar': timedelta(days=1),
                           'on_week_bar': timedelta(weeks=1)}

        self.trading_type = 'time'

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
                order.traderId = self.trader_id
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
        if self.current_time.date() < datetime.today().date():
            self.current_time += step
        else:
            time.sleep(self.step.total_seconds())

    def on_time_elapsed(self, current_time):
        logger.info('current_time:{}'.format(current_time))

    # def on_tick(self, tick_item):
    #     logger.info('on_tick:{}'.format(tick_item))
    #
    # def on_day_bar(self, bar_item):
    #     logger.info('on_day_bar:{}'.format(bar_item))

    def _get_slow_consuming_time(self):
        slow_time = None
        for k in self.level_consuming_time:
            if not slow_time:
                slow_time = self.level_consuming_time[k]
            else:
                if slow_time > self.level_consuming_time[k]:
                    slow_time = self.level_consuming_time[k]

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
                            # 设定了结束日期的话,时间到了或者kafka没数据了就结束
                            if self.end_date and (message.value[
                                                      'timestamp'] > self.end_date or message.offset + 1 == end_offset):
                                consumer.close()
                                break

                            self.level_consuming_time[func] = message.value['timestamp']

                            # 最小步长
                            if self.level_step.get(func) == self.step:
                                self.move_on(self.step)

                            # 为了准确计算当天收盘账户,必须等各级别都把当天的行情撸完了
                            while True:
                                if message.value['timestamp'] >= self._get_slow_consuming_time():
                                    time.sleep(self.step.total_seconds())

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
        # 对相应标的的行情进行监听,可以多标的多级别同时进行
        if self.universe:
            for security_id in self.universe:
                if 'on_tick' in dir(self):
                    topic = get_kafka_tick_topic(security_id)
                    if 'on_tick' in dir(self):
                        if self.level_step.get('on_tick') < self.step:
                            self.step = self.level_step.get('on_tick')
                        threading.Thread(target=self.__consume_topic_with_func, args=(topic, 'on_tick')).start()
                        self.trading_type = 'event'
                        self.level_consuming_time['on_tick'] = self.current_time
                for level in ('week', 'day', '60', '30', '15', '5', '1'):
                    the_func = 'on_{}_bar'.format(level)
                    topic = get_kafka_kdata_topic(security_id, fuquan=self.stock_fuquan)
                    if the_func in dir(self):
                        if self.level_step.get(the_func) < self.step:
                            self.step = self.level_step.get(the_func)
                        threading.Thread(target=self.__consume_topic_with_func, args=(topic, the_func)).start()
                        self.trading_type = 'event'
                        self.level_consuming_time[the_func] = self.current_time

        # 主线程,是时间漫步的方式,一般来说,step用日线就可以了,主要用在那种大级别的操作
        # 账户的每日市值更新也是在这里计算的
        while True:
            self.on_time_elapsed(self.current_time)
            current_time = self.current_time
            if self.trading_type == 'time':
                self.move_on(self.step)
            if self.current_time.day - current_time.day == 1:
                self.account_service.save_account(current_time, trading_close=True)


if __name__ == '__main__':
    trader = Trader()
    trader.run()
