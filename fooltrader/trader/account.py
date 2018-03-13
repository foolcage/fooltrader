# -*- coding: utf-8 -*-

import logging
import threading

import pandas as pd
from elasticsearch_dsl import DocType, Keyword, Float, Nested, Date, Long, Short, Boolean
from elasticsearch_dsl import MetaField

from fooltrader.api.quote import get_kdata

logger = logging.getLogger(__name__)


class AccountService(object):
    def __init__(self, trader_id, timestamp,
                 base_capital=1000000,
                 buy_cost=0.001,
                 sell_cost=0.001,
                 slippage=0.001,
                 stock_fuquan='hfq'):
        self.base_capital = base_capital
        self.buy_cost = buy_cost
        self.sell_cost = sell_cost
        self.slippage = slippage
        self.trader_id = trader_id
        self.stock_fuquan = stock_fuquan

        # 账户锁,用于保证仓位更新的原子性
        self.account_lock = threading.RLock()

        # 初始化账户
        self.account = Account()
        self.account.traderId = trader_id
        self.account.cash = base_capital
        self.account.positions = []
        self.account.allValue = base_capital
        self.account.timestamp = timestamp
        self.save_account(timestamp)

    def save_account(self, timestamp, trading_close=False):
        self.account_lock.acquire()

        self.account = self.account.copy_for_save(trading_close=trading_close)
        self.account.timestamp = timestamp
        self.account.allValue = 0
        for position in self.account.positions:
            # 对于T+1的,下个交易日all available
            if trading_close and position.tradingT == 1:
                position.availableAmount = position.amount
            df = get_kdata(position.securityId, pd.Timestamp(timestamp).date(), source='sina', fuquan=self.stock_fuquan)
            if len(df) > 0:
                position.value = position.amount * df['close']
            self.account.allValue += position.value
            if position.amount == 0:
                self.account.positions.remove(position)

        self.account.allValue += self.account.cash

        self.account.save(index='account')

        self.account_lock.release()

    def get_position(self, security_id):
        for position in self.account.positions:
            if position.securityId == security_id:
                return position
        return None

    # 对于T+1仓位的更新,当日交易结束才计算盈亏
    # Position的availableAmount也不需要更新
    def update_position(self, security_id, amount_change, pct_change, current_price, timestamp):
        logger.debug("{} acquire account lock".format(threading.current_thread().name))
        self.account_lock.acquire()
        logger.debug("{} acquire account lock success".format(threading.current_thread().name))

        current_position = None
        has_position = False
        for position in self.account.positions:
            if position.securityId == security_id:
                current_position = position
                has_position = True
        if not current_position:
            current_position = Position(security_id=security_id)

        # 按数量交易
        if amount_change != 0:
            # 买
            if amount_change > 0:
                # 不差钱
                need_money = (amount_change * current_price) * (1 + self.slippage + self.buy_cost)
                if self.account.cash >= need_money:
                    self.account.cash -= need_money
                    current_position.amount += amount_change
                else:
                    raise Exception("not enough money")
            # 卖
            elif amount_change < 0:
                # 不差货
                amount_change = abs(amount_change)
                if current_position.availableAmount >= amount_change:
                    current_position.amount -= amount_change
                    current_position.availableAmount -= amount_change
                    self.account.cash += (amount_change * current_price) * (1 - self.slippage - self.sell_cost)
                else:
                    raise Exception("not enough pos")
        # 按仓位比例交易
        elif pct_change != 0:
            if pct_change > 0:
                # 不差钱
                cost = current_price * (1 + self.slippage + self.buy_cost)
                want_buy = self.account.cash * pct_change
                if want_buy >= cost:
                    amount_change = want_buy // cost
                    self.account.cash -= (want_buy - want_buy % cost)
                    current_position.amount += amount_change
                else:
                    raise Exception("not enough money")
            elif pct_change < 0:
                # 不差货
                amount_change = current_position.amount * abs(pct_change)
                if amount_change >= 1:
                    current_position.amount -= amount_change
                    current_position.availableAmount -= amount_change
                    self.account.cash += (amount_change * current_price) * (1 - self.slippage - self.sell_cost)
                else:
                    raise Exception("not enough pos")

        if not has_position:
            self.account.positions.append(current_position)

        self.save_account(timestamp)

        self.account_lock.release()
        logger.debug("{} release account lock success".format(threading.current_thread().name))


# 一个索引对应一个账户,索引的名字就是traderId,以id为时间戳为id(精确到秒)
class Account(DocType):
    traderId = Keyword()
    cash = Float()
    positions = Nested()
    allValue = Float()
    timestamp = Date()
    tradingClose = Boolean()

    def copy_for_save(self, trading_close):
        account = Account()
        account.cash = self.cash
        account.traderId = self.traderId
        account.allValue = self.allValue
        account.positions = self.positions
        account.timestamp = account.timestamp
        account.tradingClose = trading_close
        return account

    def save(self, using=None, index=None, validate=True, **kwargs):
        self.meta.id = "{}_{}".format(self.traderId, self.timestamp.strftime('%Y-%m-%d %H:%M:%S'))
        return super().save(using, index, validate, **kwargs)

    class Meta:
        doc_type = 'doc'
        all = MetaField(enabled=False)


class Position(DocType):
    # 证券id
    securityId = Keyword()
    # 持有数量
    amount = Long()
    # 可交易数量
    availableAmount = Long()
    # 盈亏
    profit = Float()
    # 市值
    value = Float()
    # 成本价
    cost = Float()
    # 交易类型(0代表T+0,1代表T+1)
    tradingT = Short()

    def __init__(self, meta=None, security_id=None, trading_t=1, **kwargs):
        super().__init__(meta, **kwargs)
        self.securityId = security_id
        self.availableAmount = 0
        self.amount = 0
        self.profit = 0
        self.value = 0
        self.cost = 0
        self.tradingT = trading_t


class Order(DocType):
    # 订单id
    id = Keyword()
    # 交易员id
    traderId = Keyword()
    # 证券id
    securityId = Keyword()
    # 买卖(多空)
    direction = Short()
    # 市价/限价
    type = Keyword()
    # 价格
    price = Float()
    # 数量
    amount = Long()
    # 状态
    status = Keyword()
    # 时间
    timestamp = Date()

    class Meta:
        doc_type = 'doc'
        all = MetaField(enabled=False)
