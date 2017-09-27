import json
import logging

from kafka import KafkaConsumer

from fooltrader.domain.Account import Account, Order
from fooltrader.utils.data_contract import get_kafka_kdata_topic

logger = logging.getLogger(__name__)


class Trader(object):
    account = Account()

    baseCapital = 1000000;
    buyCost = 0.001;
    sellCost = 0.001;
    slippage = 0.001;

    start = '2015-1-1'
    end = '2017-9-25'

    universe = ('sh_stock_600000', 'sz_stock_600004')

    trader_id = 'fool1'

    def buy(self, security_id, amount, current_price=0, order_price=0):
        # 市价交易
        if order_price == 0:
            order = Order()
            order.save()

    def run(self):
        for security_id in self.universe:
            consumer = KafkaConsumer(get_kafka_kdata_topic(security_id),
                                     auto_offset_reset='earliest',
                                     group_id=self.trader_id,
                                     value_deserializer=lambda m: json.loads(m.decode('ascii')),
                                     bootstrap_servers=['localhost:9092'])
            for message in consumer:
                logger.info(message.value)


trader = Trader()
trader.run()
