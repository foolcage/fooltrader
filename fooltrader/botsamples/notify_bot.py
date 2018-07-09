# -*- coding: utf-8 -*-
from datetime import timedelta, datetime

from fooltrader.api.quote import get_kdata
from fooltrader.bot.actions import EmailAction, WeixinAction
from fooltrader.bot.base_bot import BaseBot
from fooltrader.datasource.ccxt_wrapper import fetch_kdata
from fooltrader.domain.subscription_model import SubscriptionTriggered, PriceSubscription
from fooltrader.utils.utils import is_same_date, to_timestamp, to_time_str


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
        self.has_triggered = {}

        s = PriceSubscription.search()

        s = s.filter('term', securityType=self.security_item['type']) \
            .filter('term', exchange=self.security_item['exchange'])
        results = s.execute()

        for hit in results['hits']['hits']:
            self.subscriptions[hit['_id']] = hit['_source'].to_dict()

        # 查询该标的的价格提醒订阅
        self.update_today_triggered()

        self.email_action = EmailAction()
        self.weixin_action = WeixinAction()

    # 查询当日已经发送的提醒
    def update_today_triggered(self):
        sub_triggered_search = SubscriptionTriggered.search()

        sub_triggered_search = sub_triggered_search.filter('term', subType='price') \
            .filter('range', timestamp={'gte': to_time_str(datetime.now())})
        results = sub_triggered_search.execute()

        for hit in results['hits']['hits']:
            json_data = hit['_source'].to_dict()
            self.has_triggered["{}_{}".format(json_data['subId'], json_data['conditionType'])] = json_data

    # 监听订阅事件
    def on_subscription(self, event_item):
        self.logger.info("on_subscription:{}".format(event_item))
        self.subscriptions[event_item['_id']] = event_item['_source']

    # 监听行情
    def on_event(self, event_item):
        self.logger.debug(event_item)
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

            self.update_today_triggered()

        change_pct = (self.last_close - event_item['price']) / self.last_close

        self.logger.info(
            "{} last day close is:{},now price is:{},the change_pct is:{}".format(self.security_item['id'],
                                                                                  self.last_close,
                                                                                  event_item['price'], change_pct))
        self.check_subscription(current_price=event_item['price'], change_pct=change_pct)

    def handle_trigger(self, trigger_flag, sub_id, subscription, current_price, change_pct):
        triggered = False
        if trigger_flag not in self.has_triggered:
            sub_triggerd = SubscriptionTriggered(sub_id=sub_id, timestamp=self.current_time, conditionType='up')
            sub_triggerd.save(index='subscription_triggered')

            triggered = True

            self.logger.debug(
                "send msg to user:{},price:{},change_pct:{}".format(subscription['userId'], current_price,
                                                                    change_pct))

            if 'weixin' in subscription['actions']:
                self.weixin_action.send_message(subscription['userId'], title="价格条件触发", body=None,
                                                name=self.security_item['name'], price=current_price,
                                                change_pct='{:.2%}'.format(change_pct))

        if triggered:
            self.has_triggered[trigger_flag] = sub_triggerd.to_dict()
            self.logger.info("trigger:{} happen".format(trigger_flag))

    def check_subscription(self, current_price, change_pct):

        for sub_id in self.subscriptions.keys():
            subscription = self.subscriptions[sub_id]

            if change_pct > 0 and subscription.get('up') and current_price > subscription.get('up'):
                triggered_flag = "{}_{}".format(sub_id, 'up')

                self.handle_trigger(triggered_flag, sub_id, subscription, current_price, change_pct)

            if change_pct < 0 and subscription.get('down') and current_price < subscription.get('down'):
                triggered_flag = "{}_{}".format(sub_id, 'down')
                self.handle_trigger(triggered_flag, sub_id, subscription, current_price, change_pct)

            if change_pct > 0 and subscription.get('upPct') and change_pct > subscription.get('upPct'):
                triggered_flag = "{}_{}".format(sub_id, 'upPct')
                self.handle_trigger(triggered_flag, sub_id, subscription, current_price, change_pct)

            if change_pct < 0 and subscription.get('downPct') and change_pct < subscription.get('downPct'):
                triggered_flag = "{}_{}".format(sub_id, 'downPct')
                self.handle_trigger(triggered_flag, sub_id, subscription, current_price, change_pct)


if __name__ == '__main__':
    NotifyBot().run()
