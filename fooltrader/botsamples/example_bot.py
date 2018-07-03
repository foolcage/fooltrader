# -*- coding: utf-8 -*-
from datetime import timedelta

from fooltrader.api.quote import get_kdata
from fooltrader.bot.base_bot import BaseBot
from fooltrader.domain.subscription import Subscription
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


class ExampleBot(BaseBot):
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
        s = Subscription.search()

        s = s.filter('term', securityType=self.security_item['type']).filter('term',
                                                                             exchange=self.security_item['exchange'])
        results = s.execute()

        self.subscriptions = [hit.to_dict() for hit in results.hits]

    def on_subscription(self, event_item):
        self.subscriptions[event_item['id']] = event_item

    def on_event(self, event_item):
        # self.logger.info(event_item)
        if not self.last_date or not is_same_date(self.last_date, self.current_time / 1000):
            self.last_date = to_timestamp(event_item['timestamp'] / 1000) - timedelta(days=1)
            self.last_kdata = get_kdata(self.security_item, the_date=to_time_str(self.last_date))
            self.last_close = self.last_kdata.loc[to_time_str(self.last_date), 'close']

        change_pct = (self.last_close - event_item['price']) / self.last_close

        if abs(change_pct) >= 0.01:
            self.logger.warning(
                "{} last day close is:{},now price is:{},the change_pct is:{}".format(self.security_item['id'],
                                                                                      self.last_close,
                                                                                      event_item['price'], change_pct))
        self.check_condition(current_price=event_item['price'], change_pct=change_pct)

    def check_condition(self, current_price, change_pct):
        for sub in self.subscriptions:
            if change_pct > 0 and sub.get('up') and sub.get('up') > current_price:
                msg = "{} up to {}".format(self.security_item['id'], current_price)
                self.logger.info("notify to:{},msg:{}".format(sub['userId'], msg))

            if change_pct < 0 and sub.get('down') and sub.get('down') < current_price:
                msg = "{} down to {}".format(self.security_item['id'], current_price)
                self.logger.info("notify to:{},msg:{}".format(sub['userId'], msg))

            if change_pct > sub.get['upPct']:
                msg = "{} up {}".format(self.security_item['id'], change_pct)
                self.logger.info("notify to:{},msg:{}".format(sub['userId'], msg))

            if change_pct < sub.get['downPct']:
                msg = "{} down {}".format(self.security_item['id'], change_pct)
                self.logger.info("notify to:{},msg:{}".format(sub['userId'], msg))


if __name__ == '__main__':
    ExampleBot().run()
