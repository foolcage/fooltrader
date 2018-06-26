# -*- coding: utf-8 -*-
import random

from fooltrader.bot.base_bot import QuoteTradingBot


class RandomBot(QuoteTradingBot):

    def on_init(self):
        super().on_init()
        self.security_item = '300027'

    def on_event(self, event_item):
        try:
            if random.randint(0, 9) % 2 == 0:
                self.account_service.buy(self.security_item['id'], current_price=event_item['close'])
            else:
                self.account_service.close_long(self.security_item['id'], current_price=event_item['close'])
        except Exception as e:
            self.logger.warning(e)


if __name__ == '__main__':
    RandomBot().run()
