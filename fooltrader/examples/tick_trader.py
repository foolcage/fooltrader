# -*- coding: utf-8 -*-

import pandas as pd

from fooltrader.api.quote import get_kdata
from fooltrader.trader.trader import Trader
from fooltrader.utils.utils import is_same_date, index_df_with_time


class TickTrader(Trader):
    def on_init(self):
        self.trader_id = 'bb'
        self.only_event_mode = True
        self.universe = ['stock_sz_000002']
        self.today_traded = False
        self.df = pd.DataFrame()

    def on_tick(self, tick_item):
        # 只计算日内,超短线
        if not is_same_date(self.current_time, tick_item['timestamp']):
            self.today_traded = False
            if not self.df.empty:
                self.df = pd.DataFrame()
        else:
            if not self.today_traded:
                if not self.df.empty and self.df.index.size == 1:
                    self.df = index_df_with_time(self.df)
                self.df = self.df.append(tick_item, ignore_index=True)
                # 14:50时,计算当日资金流
                if ("14:50:" in tick_item['timestamp']):
                    money_flow = (self.df['turnover'] * self.df['direction']).sum()
                    money_all = (self.df['turnover'] * abs(self.df['direction'])).sum()

                    # 净流入
                    if money_flow > 0 and not self.account_service.get_position(tick_item['securityId']):
                        # 使用用后复权价格
                        factor = \
                            get_kdata(tick_item['securityId'], the_date=pd.Timestamp(tick_item['timestamp']).date())[
                                'factor']
                        self.buy(tick_item['securityId'], current_price=tick_item['price'] * factor)
                    # 净流出
                    elif money_flow < 0 and self.account_service.get_position(tick_item['securityId']):
                        # 使用用后复权价格
                        factor = \
                            get_kdata(tick_item['securityId'], the_date=pd.Timestamp(tick_item['timestamp']).date())[
                                'factor']
                        self.sell(tick_item['securityId'], current_price=tick_item['price'] * factor)
                    self.today_traded = True


def run():
    from elasticsearch_dsl.connections import connections

    connections.create_connection(hosts=['localhost'], timeout=20)

    TickTrader().run()


if __name__ == '__main__':
    run()
