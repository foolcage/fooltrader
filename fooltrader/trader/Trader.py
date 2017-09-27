from kafka import KafkaConsumer

from fooltrader.fooltrader import Account, Order


class Trader(object):
    account = Account()

    baseCapital = 1000000;
    buyCost = 0.001;
    sellCost = 0.001;
    slippage = 0.001;

    start = '2015-1-1'
    end = '2017-9-25'

    universe = ('sz_stock_000338', 'sz_stock_000778')

    def buy(self, security_id, amount, current_price=0, order_price=0):
        # 市价交易
        if order_price == 0:
            order = Order()
            order.save()

    def run(self):
        for security_id in self.universe:
            consumer = KafkaConsumer('my-topic',
                                     group_id='my-group',
                                     bootstrap_servers=['localhost:9092'])
