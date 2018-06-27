# -*- coding: utf-8 -*-
from datetime import timedelta

from fooltrader.api.quote import get_kdata
from fooltrader.bot.base_bot import BaseBot
from fooltrader.utils.utils import is_same_date, to_timestamp, to_time_str


class ExampleBot(BaseBot):
    def on_init(self):
        self.need_account = False
        self.security_item = 'cryptocurrency_kraken_BCH-USD'
        self.level = 'tick'

        self.last_date = None
        self.last_close = None

        self.end_date = None

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


if __name__ == '__main__':
    ExampleBot().run()
