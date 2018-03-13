# -*- coding: utf-8 -*-

from fooltrader.api import quote, technical
from fooltrader.trader.trader import Trader


class TimeTrader(Trader):
    def on_init(self):
        self.trader_id = 'cc'
        self.security_code = '000002'
        self.macd = technical.macd(security_item=self.security_code, start_date=self.start_date, end_date=self.end_date,
                                   fuquan='hfq', source='sina')

    def on_time_elapsed(self):
        super().on_time_elapsed()
        current_kdata = quote.get_kdata(security_item=self.security_code, the_date=self.current_time, fuquan='hfq',
                                        source='sina')

        if len(current_kdata) > 0:
            # macd为正
            if self.macd.loc[self.current_time, 'macd'] > 0 and not self.account_service.get_position(
                    self.security_code):
                self.buy(security_id=self.security_code, current_price=current_kdata['close'], pct=1.0)
            # macd为负
            elif self.macd.loc[self.current_time, 'macd'] < 0 and self.account_service.get_position(self.security_code):
                self.sell(security_id=self.security_code, current_price=current_kdata['close'], pct=1.0)


def run():
    from elasticsearch_dsl.connections import connections

    connections.create_connection(hosts=['localhost'], timeout=20)

    TimeTrader().run()


if __name__ == '__main__':
    run()
