import pandas as pd

from fooltrader.trader.trader import Trader


class EventTrader(Trader):
    def __init__(self):
        super().__init__()
        self.universe = ['stock_sz_000001', 'stock_sz_000002']

    def on_day_bar(self, bar_item):
        df = pd.DataFrame()
        df = df.append(bar_item, ignore_index=True)
        print(df)

    def on_5_bar(self, bar_item):
        df = pd.DataFrame()
        df = df.append(bar_item, ignore_index=True)
        print(df)


if __name__ == '__main__':
    from elasticsearch_dsl.connections import connections

    connections.create_connection(hosts=['localhost'], timeout=20)

    EventTrader().run()
