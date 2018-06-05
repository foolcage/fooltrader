# -*- coding: utf-8 -*-
import random

from fooltrader.bot.event_bot import QuoteEventBot


class RandomBot(QuoteEventBot):
    security_item = '300027'

    def on_event(self, event_item):
        try:
            if random.randint(0, 9) % 2 == 0:
                self.buy(self.security_item['id'], current_price=event_item['close'])
            else:
                self.close_long(self.security_item['id'], current_price=event_item['close'])
        except Exception as e:
            self.logger.warning(e)


if __name__ == '__main__':
    RandomBot().run()
