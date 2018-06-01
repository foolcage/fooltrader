# -*- coding: utf-8 -*-

import logging

import pandas as pd

from fooltrader.domain.account import Account, Position
from fooltrader.utils.es_utils import es_get_latest_record


class BaseBot(object):
    def on_init(self):
        pass

    def _after_init(self):
        if type(self.start_date) == str:
            self.start_date = pd.Timestamp(self.start_date)
        if type(self.end_date) == str:
            self.end_date = pd.Timestamp(self.end_date)

        # 时间点
        self.current_time = pd.Timestamp(self.start_date)

        self._create_account(self.bot_name)

    def _create_account(self, botName):
        self.account = es_get_latest_record(index='account', query={"term": {"botName": botName}})

        if self.account:
            self.logger.warning("bot:{} has run before,old result would be deleted".format(botName))
            self.account.delete(index='account', query={"term": {"botName": botName}})

        self.account = Account()
        self.account.botName = botName
        self.account.cash = self.base_capital
        self.account.positions = []
        self.account.allValue = self.base_capital
        self.account.timestamp = self.start_date
        self.account.save()

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        self.base_capital = 1000000;
        self.buy_cost = 0.001;
        self.sell_cost = 0.001;
        self.slippage = 0.001;

        # 回测的开始日期
        self.start_date = pd.Timestamp('2013-01-01')
        # 回测的结束日期,为None的话会一直运行
        self.end_date = pd.Timestamp.today()

        self.bot_name = type(self).__name__.lower()

        self.on_init()

        self._after_init()

    def get_current_account(self):
        self.account = es_get_latest_record(index='account', query={"term": {"botName": self.bot_name}})
        return self.account

    def get_position(self, security_id):
        for position in self.account.positions:
            if position.securityId == security_id:
                return position
        return Position(security_id=security_id)

    def update_position(self, security_id, new_position):
        positions = [position for position in self.account.positions if position.securityId != security_id]

        positions.append(new_position)

    # 开多,对于某些品种只能开多，比如中国股票
    def do_long(self, security_id, current_price, amount=0, pct=1.0, order_price=0):
        """
        对每个投资标的开多.

        Parameters
        ----------
        security_id : str
            交易标的id

        current_price : float
            当前价格

        amount : int
            数量

        pct : float
            使用可用现金的百分比,0.0-1.0

        order_price : float
            用于限价交易

        Returns
        -------


        """

        # 市价交易,就是买卖是"当时"并"一定"能成交的
        # 简单起见，目前只支持这种方式
        if order_price == 0:
            current_position = self.get_position(security_id=security_id)

            # 按数量交易
            if amount > 0:
                # 不差钱
                need_money = (amount * current_price) * (1 + self.slippage + self.buy_cost)
                if self.account.cash >= need_money:
                    self.account.cash -= need_money
                    current_position.longAmount += amount
                else:
                    raise Exception("not enough money")
            # 按仓位比例交易
            elif pct > 0 and pct <= 1:
                # 不差钱
                cost = current_price * (1 + self.slippage + self.buy_cost)
                want_buy = self.account.cash * pct
                if want_buy >= cost:
                    # 买的数量
                    amount = want_buy // cost
                    # 使用的现金
                    self.account.cash -= (want_buy - want_buy % cost)
                    current_position.longAmount += amount
                else:
                    raise Exception("not enough money")

            self.update_position(current_position)

    # 开空
    def do_short(self, security_id, current_price, amount=0, pct=1.0, order_price=0):
        # 市价交易,就是买卖是"当时"并"一定"能成交的
        # 简单起见，目前只支持这种方式
        if order_price == 0:
            current_position = None
            has_position = False
            for position in self.account.positions:
                if position.securityId == security_id:
                    current_position = position
                    has_position = True
            if not current_position:
                current_position = Position(security_id=security_id)

            # 按数量交易
            if amount > 0:
                # 不差钱
                need_money = (amount * current_price) * (1 + self.slippage + self.buy_cost)
                if self.account.cash >= need_money:
                    self.account.cash -= need_money
                    current_position.longAmount += amount
                else:
                    raise Exception("not enough money")
            # 按仓位比例交易
            elif pct > 0 and pct <= 1:
                # 不差钱
                cost = current_price * (1 + self.slippage + self.buy_cost)
                want_buy = self.account.cash * pct
                if want_buy >= cost:
                    # 买的数量
                    amount = want_buy // cost
                    # 使用的现金
                    self.account.cash -= (want_buy - want_buy % cost)
                    current_position.longAmount += amount
                else:
                    raise Exception("not enough money")

            if not has_position:
                self.account.positions.append(current_position)

    # 平仓
    def liquidate(self, security_id, current_price, amount=0, pct=1.0, order_price=0):
        pass
