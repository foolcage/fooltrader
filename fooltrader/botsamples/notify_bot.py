# -*- coding: utf-8 -*-
from datetime import timedelta

from kafka import KafkaProducer

from fooltrader.api.quote import get_kdata
from fooltrader.bot.actions import EmailAction
from fooltrader.bot.base_bot import BaseBot
from fooltrader.datasource.ccxt_wrapper import fetch_kdata
from fooltrader.domain.subscription import PriceSubscription, SubscriptionTriggered
from fooltrader.settings import KAFKA_HOST
from fooltrader.utils.utils import is_same_date, to_timestamp, to_time_str

{
    "id": 123,
    "userId": 111,
    "securityType": "cryptocurrency",
    "exchange": "binance",
    "code": "BTC-USDT",
    "condition": {
        "upPct": 1,
        "downPct": 2,
        "up": 7000,
        "down": 6000,
        "cross": 0.02
    },
    "repeat": False
}

producer = KafkaProducer(bootstrap_servers=KAFKA_HOST)


class NotifyBot(BaseBot):
    def on_init(self):
        # 设置为True会创建AccountService,可使用self.account_service进行买卖，系统会计算收益
        # 设置为False,就没有账户信息
        self.need_account = False

        # 设置投资标的，会在on_event里面接收到该标的的行情
        self.security_item = 'cryptocurrency_kraken_BCH-USD'
        # 行情的级别
        self.level = 'tick'
        # bot运行的结束时间，设置为None将会一直运行
        self.end_date = None

        # 自定义字段放这里
        self.last_date = None
        self.last_close = None

    def after_init(self):
        self.subscriptions = {}
        self.has_triggered = []
        s = PriceSubscription.search()

        s = s.filter('term', securityType=self.security_item['type']) \
            .filter('term', exchange=self.security_item['exchange'])
        results = s.execute()

        for hit in results['hits']['hits']:
            self.subscriptions[hit['_id']] = hit['_source'].to_dict()

        self.email_action = EmailAction()

    def on_subscription(self, event_item):
        self.logger.info("on_subscription:{}".format(event_item))
        self.subscriptions[event_item['_id']] = event_item['_source']

    def on_event(self, event_item):
        # self.logger.info(event_item)
        if not self.last_date or not is_same_date(self.last_date, self.current_time):
            self.last_date = to_timestamp(event_item['timestamp']) - timedelta(days=1)
            self.last_kdata = get_kdata(self.security_item, the_date=to_time_str(self.last_date))

            if self.last_kdata is None:
                fetch_kdata(exchange_str=self.security_item['exchange'])
                self.last_kdata = get_kdata(self.security_item, the_date=to_time_str(self.last_date))

            if self.last_kdata is not None:
                self.last_close = self.last_kdata.loc[to_time_str(self.last_date), 'close']
            else:
                self.logger.error("could not get last close for:{}".format(self.last_date))

        change_pct = (self.last_close - event_item['price']) / self.last_close

        self.logger.info(
            "{} last day close is:{},now price is:{},the change_pct is:{}".format(self.security_item['id'],
                                                                                  self.last_close,
                                                                                  event_item['price'], change_pct))
        self.check_condition(current_price=event_item['price'], change_pct=change_pct)

    def check_condition(self, current_price, change_pct):
        triggered = []
        for sub_id in self.subscriptions:
            sub = self.subscriptions[sub_id]
            condition = sub['condition']

            if change_pct > 0 and condition.get('up') and condition.get('up') > current_price:
                msg = "{} up to {}".format(self.security_item['id'], current_price)
                self.logger.info("notify to user:{},msg:{}".format(sub['userId'], msg))
                if "email" in sub:
                    self.email_action.send_message(sub['email'], "price notification", msg)

            if change_pct < 0 and condition.get('down') and condition.get('down') < current_price:
                msg = "{} down to {}".format(self.security_item['id'], current_price)
                self.logger.info("notify to user:{},msg:{}".format(sub['userId'], msg))
                if "email" in sub:
                    self.email_action.send_message(sub['email'], "price notification", msg)

            if change_pct > 0 and condition.get('upPct') and change_pct > condition.get('upPct'):
                msg = "{} up {}".format(self.security_item['id'], change_pct)
                self.logger.info("notify to user:{},msg:{}".format(sub['userId'], msg))
                if "email" in sub:
                    self.email_action.send_message(sub['email'], "price notification", msg)

            if change_pct < 0 and condition.get('downPct') and change_pct < condition.get('downPct'):
                msg = "{} down {}".format(self.security_item['id'], change_pct)
                self.logger.info("notify to user:{},msg:{}".format(sub['userId'], msg))
                if "email" in sub:
                    self.email_action.send_message(sub['email'], "price notification", msg)

            st = SubscriptionTriggered(sub_id=sub_id, timestamp=self.current_time)
            st.save(index='subscription_triggered')
            triggered.append(sub_id)
        if self.subscriptions:
            self.subscriptions = [v for k, v in self.subscriptions.items() if (v['repeat'] or k not in triggered)]


if __name__ == '__main__':
    NotifyBot().run()
