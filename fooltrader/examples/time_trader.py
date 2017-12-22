from fooltrader.api import quote
from fooltrader.computing import technical
from fooltrader.trader.trader import Trader


class TimeTrader(Trader):
    def __init__(self):
        super().__init__()
        self.security_code = '000001'

    def on_time_elapsed(self):
        super().on_time_elapsed()
        current_kdata = quote.get_kdata(security_item=self.security_code, the_date=self.current_time)
        if len(current_kdata) > 0:
            the_close = current_kdata['close']
            print(the_close)
            the_ma = technical.ma(self.security_code, start=self.current_time, end=self.current_time)['close_ma5'][0]
            print(the_ma)
            # 站上5日线,并且没仓位
            if the_close > the_ma and not self.account_service.get_position(self.security_code):
                self.buy(security_id=self.security_code, current_price=the_close, pct=1.0)
            # 跌破5日线,并且有仓位
            elif the_close < the_ma and self.account_service.get_position(self.security_code):
                self.sell(security_id=self.security_code, current_price=the_close, pct=1.0)


if __name__ == '__main__':
    from elasticsearch_dsl.connections import connections

    connections.create_connection(hosts=['localhost'], timeout=20)

    TimeTrader().run()
