# -*- coding: utf-8 -*-
import time

import schedule

from fooltrader.bot.bot import SoloBot
from fooltrader.trader.model import CrossMaModel


class MaBot(SoloBot):
    trading_model = CrossMaModel()

    def fetch_kdata(self):
        self.trading_model.append_data()

    def run(self):
        schedule.every(1).minutes.do(self.fetch_kdata)

        while True:
            schedule.run_pending()
            time.sleep(1)
