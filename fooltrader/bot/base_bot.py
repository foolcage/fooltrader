# -*- coding: utf-8 -*-

import logging
import math

import pandas as pd

from fooltrader.api import esapi
from fooltrader.domain.account import Account, Position
from fooltrader.utils.es_utils import es_get_latest_record, es_delete, es_index_mapping
from fooltrader.utils.utils import fill_doc_type

ORDER_TYPE_LONG = 0
ORDER_TYPE_SHORT = 1
ORDER_TYPE_CLOSE_LONG = 2
ORDER_TYPE_CLOSE_SHORT = 3


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

        self._init_account()

    def _init_account(self):
        account = es_get_latest_record(index='account', query={"term": {"botName": self.bot_name}})

        if account:
            self.logger.warning("bot:{} has run before,old result would be deleted".format(self.bot_name))
            es_delete(index='account', query={"term": {"botName": self.bot_name}})

        es_index_mapping('account', Account)

        self.account = Account()
        self.account.botName = self.bot_name
        self.account.cash = self.base_capital
        self.account.positions = []
        self.account.allValue = self.base_capital
        self.account.timestamp = self.start_date
        self.account.save()

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        self.base_capital = 1000000
        self.buy_cost = 0.001
        self.sell_cost = 0.001
        self.slippage = 0.001

        # 回测的开始日期
        self.start_date = pd.Timestamp('2013-01-01')
        # 回测的结束日期,为None的话会一直运行
        self.end_date = pd.Timestamp.today()

        self.bot_name = type(self).__name__.lower()

        self.on_init()

        self._after_init()

    def get_account(self, refresh=True):
        if refresh:
            account_json = es_get_latest_record(index='account', query={"term": {"botName": self.bot_name}})
            self.account = Account()
            fill_doc_type(self.account, account_json)

        return self.account

    def get_current_position(self, security_id):
        account = self.get_account()
        for position in account.positions:
            if position.securityId == security_id:
                return position
        return Position(security_id=security_id)

    # 计算收盘账户
    def calculate_closing_account(self):
        account = self.get_account()
        for position in account.positions:
            closing_price = esapi.get_kdata(security_item=position['securityId'], the_date=self.current_time)
            position.availableLong = position.longAmount
            position.availableShort = position.shortAmount
            position.profit

    # 两种情况下会被调用：
    # 1)操作导致账户更新
    # 2)当日收盘
    def save_account(self):
        self.account.save()

    def update_position(self, security_id, new_position):
        # 先去掉之前的position
        positions = [position for position in self.account.positions if position.securityId != security_id]
        # 更新为新的position
        positions.append(new_position)
        self.account.positions = positions
        self.account.save()

    # 开多,对于某些品种只能开多，比如中国股票
    def buy(self, security_id, current_price, order_amount=0, order_pct=1.0, order_price=0):
        self.order(security_id, current_price, order_amount, order_pct, order_price, order_type=ORDER_TYPE_LONG)

    # 开空
    def sell(self, security_id, current_price, order_amount=0, order_pct=1.0, order_price=0):
        self.order(security_id, current_price, order_amount, order_pct, order_price, order_type=ORDER_TYPE_SHORT)

    # 平多
    def close_long(self, security_id, current_price, order_amount=0, order_pct=1.0, order_price=0):
        self.order(security_id, current_price, order_amount, order_pct, order_price, order_type=ORDER_TYPE_CLOSE_LONG)

    # 平空
    def close_short(self, security_id, current_price, order_amount=0, order_pct=1.0, order_price=0):
        self.order(security_id, current_price, order_amount, order_pct, order_price, order_type=ORDER_TYPE_CLOSE_SHORT)

    def order(self, security_id, current_price, order_amount=0, order_pct=1.0, order_price=0,
              order_type=ORDER_TYPE_LONG):
        """
        对每个投资标的开多.

        Parameters
        ----------
        security_id : str
            交易标的id

        current_price : float
            当前价格

        order_amount : int
            数量

        order_pct : float
            使用可用现金的百分比,0.0-1.0

        order_price : float
            用于限价交易

        order_type : {ORDER_TYPE_LONG,ORDER_TYPE_SHORT,ORDER_TYPE_CLOSE_LONG,ORDER_TYPE_CLOSE_SHORT}
            交易类型

        Returns
        -------


        """

        # 市价交易,就是买卖是"当时"并"一定"能成交的
        # 简单起见，目前只支持这种方式
        if order_price == 0:
            current_position = self.get_current_position(security_id=security_id)

            # 按数量交易
            if order_amount > 0:
                # 开多
                if order_type == ORDER_TYPE_LONG:
                    need_money = (order_amount * current_price) * (1 + self.slippage + self.buy_cost)
                    if self.account.cash >= need_money:
                        self.account.cash -= need_money
                        current_position.longAmount += order_amount
                        if current_position.tradingT == 0:
                            current_position.availableLong += order_amount
                    else:
                        raise Exception("not enough money")
                # 开空
                elif order_type == ORDER_TYPE_SHORT:
                    need_money = (order_amount * current_price) * (1 + self.slippage + self.buy_cost)
                    if self.account.cash >= need_money:
                        self.account.cash -= need_money
                        current_position.shortAmount += order_amount
                        if current_position.tradingT == 0:
                            current_position.availableShort += order_amount

                    else:
                        raise Exception("not enough money")
                # 平多
                elif order_type == ORDER_TYPE_CLOSE_LONG:
                    if current_position.availableLong >= order_amount:
                        self.account.cash += (order_amount * current_price)
                        current_position.availableLong -= order_amount
                        current_position.longAmount -= order_amount
                    else:
                        raise Exception("not enough position")
                # 平空
                elif order_type == ORDER_TYPE_CLOSE_SHORT:
                    if current_position.availableShort >= order_amount:
                        self.account.cash += (order_amount * current_price)
                        current_position.availableShort -= order_amount
                        current_position.shortAmount -= order_amount
                    else:
                        raise Exception("not enough position")

            # 按仓位比例交易
            elif 0 < order_pct <= 1:
                # 开多
                if order_type == ORDER_TYPE_LONG:
                    cost = current_price * (1 + self.slippage + self.buy_cost)
                    want_buy = self.account.cash * order_pct
                    if want_buy >= cost:
                        # 买的数量
                        order_amount = want_buy // cost
                        # 使用的现金
                        self.account.cash -= (want_buy - want_buy % cost)
                        current_position.longAmount += order_amount
                        if current_position.tradingT == 0:
                            current_position.availableLong += order_amount
                    else:
                        raise Exception("not enough money")
                # 开空
                elif order_type == ORDER_TYPE_SHORT:
                    need_money = (order_amount * current_price) * (1 + self.slippage + self.buy_cost)
                    if self.account.cash >= need_money:
                        self.account.cash -= need_money
                        current_position.shortAmount += order_amount
                        if current_position.tradingT == 0:
                            current_position.availableShort += order_amount
                    else:
                        raise Exception("not enough money")
                # 平多
                elif order_type == ORDER_TYPE_CLOSE_LONG:
                    if current_position.availableLong > 1:
                        order_amount = math.floor(current_position.availableLong * order_pct)
                        if order_amount != 0:
                            self.account.cash += (order_amount * current_price)
                            current_position.availableLong -= order_amount
                            current_position.longAmount -= order_amount
                        else:
                            self.logger.warning("{} availableLong:{} order_pct:{} order_amount:{}", security_id,
                                                current_position.availableLong, order_pct, order_amount)
                    else:
                        raise Exception("not enough position")
                # 平空
                elif order_type == ORDER_TYPE_CLOSE_SHORT:
                    if current_position.availableShort > 1:
                        order_amount = math.floor(current_position.availableShort * order_pct)
                        if order_amount != 0:
                            self.account.cash += (order_amount * current_price)
                            current_position.availableLong -= order_amount
                            current_position.longAmount -= order_amount
                        else:
                            self.logger.warning("{} availableLong:{} order_pct:{} order_amount:{}", security_id,
                                                current_position.availableLong, order_pct, order_amount)
                    else:
                        raise Exception("not enough position")

            self.update_position(security_id, current_position)
