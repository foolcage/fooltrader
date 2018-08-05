# -*- coding: utf-8 -*-
from datetime import timedelta, datetime

from fooltrader.api.esapi import esapi
from fooltrader.bot.bot import NotifyEventBot
from fooltrader.datasource.ccxt_wrapper import fetch_kdata
from fooltrader.domain.business.es_subscription import SubscriptionTriggered
from fooltrader.utils.utils import to_timestamp, to_time_str, is_same_date


class PriceNotifyBot(NotifyEventBot):
    def on_init(self):
        super().on_init()
        self.notify_weixin = True

    def after_init(self):
        # set your custom states here
        self.last_date = None
        self.last_close = None

        self.subscriptions = {}
        self.has_triggered = {}

        # 查询该标的的价格提醒订阅
        subscription_payload = esapi.es_get_subscription(security_id=self.security_id, from_idx=0, size=100000)

        self.logger.info("{} subscription count to:{}".format(self.security_id, subscription_payload['total']))
        self.subscriptions = subscription_payload['data']

        # 查询当日已经发送的提醒
        self.update_today_triggered()

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
        self.subscriptions[event_item['id']] = event_item

    # 监听行情
    def on_event(self, event_item):
        self.logger.debug(event_item)
        if not self.last_date or not is_same_date(self.last_date, self.current_time):
            self.last_date = to_timestamp(event_item['timestamp']) - timedelta(days=1)
            self.last_kdata = esapi.es_get_kdata(self.security_item, the_date=to_time_str(self.last_date))

            if self.last_kdata is None:
                fetch_kdata(exchange_str=self.security_item['exchange'])
                self.last_kdata = esapi.es_get_kdata(self.security_item, the_date=to_time_str(self.last_date))

            if self.last_kdata is not None:
                self.last_close = self.last_kdata.loc[to_time_str(self.last_date), 'close']
            else:
                self.last_close = event_item['price']
                self.logger.warn(
                    "could not get last close for:{},use:{}".format(self.last_date, event_item['timestamp']))

            self.update_today_triggered()

        change_pct = (event_item['price'] - self.last_close) / self.last_close

        self.logger.info(
            "{} last day close is:{},now price is:{},the change_pct is:{}".format(self.security_item['id'],
                                                                                  self.last_close,
                                                                                  event_item['price'], change_pct))
        self.check_subscription(current_price=event_item['price'], change_pct=change_pct)

    def handle_trigger(self, trigger_flag, sub_id, subscription, current_price, change_pct, condition_type):
        if trigger_flag not in self.has_triggered:
            sub_triggerd = SubscriptionTriggered(sub_id=sub_id, timestamp=self.current_time,
                                                 conditionType=condition_type)
            sub_triggerd.save(index='subscription_triggered')

            self.logger.debug(
                "send msg to user:{},price:{},change_pct:{}".format(subscription['userId'], current_price,
                                                                    change_pct))

            if 'weixin' in subscription['actions']:
                self.weixin_action.send_price_notification(subscription['userId'],
                                                           security_name=self.security_item['name'],
                                                           current_price=current_price,
                                                           change_pct=change_pct)
                self.has_triggered[trigger_flag] = sub_triggerd.to_dict()
                self.logger.info("trigger:{} happen".format(trigger_flag))

    def check_subscription(self, current_price, change_pct):

        for sub_id in self.subscriptions.keys():
            subscription = self.subscriptions[sub_id]

            if change_pct > 0 and subscription.get('upTo') and current_price >= subscription.get('upTo'):
                triggered_flag = "{}_{}".format(sub_id, 'upTo')

                self.handle_trigger(triggered_flag, sub_id, subscription, current_price, change_pct, 'upTo')

            if change_pct < 0 and subscription.get('downTo') and current_price <= subscription.get('downTo'):
                triggered_flag = "{}_{}".format(sub_id, 'downTo')
                self.handle_trigger(triggered_flag, sub_id, subscription, current_price, change_pct, 'downTo')

            if change_pct > 0 and subscription.get('upPct') and change_pct >= subscription.get('upPct'):
                triggered_flag = "{}_{}".format(sub_id, 'upPct')
                self.handle_trigger(triggered_flag, sub_id, subscription, current_price, change_pct, 'upPct')

            if change_pct < 0 and subscription.get('downPct') and change_pct <= subscription.get('downPct'):
                triggered_flag = "{}_{}".format(sub_id, 'downPct')
                self.handle_trigger(triggered_flag, sub_id, subscription, current_price, change_pct, 'downPct')


if __name__ == '__main__':
    PriceNotifyBot().run()
