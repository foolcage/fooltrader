# -*- coding: utf-8 -*-
from fooltrader.bot.bot import Bot


class BasicMaBot(Bot):
    def on_init(self):
        self.target = '300027'


if __name__ == '__main__':
    from elasticsearch_dsl.connections import connections

    connections.create_connection(hosts=['localhost'], timeout=20)

    BasicMaBot().run()
