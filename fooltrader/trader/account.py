from elasticsearch_dsl import DocType, Keyword, Float, Nested, Date, Long, Short
from elasticsearch_dsl import MetaField


class Account(DocType):
    traderId = Keyword()
    cash = Float()
    positions = Nested()
    timestamp = Date()

    transaction_setting = {}

    def __init__(self, base_capital=1000000,
                 buy_cost=0.001,
                 sell_cost=0.001,
                 slippage=0.001, meta=None, **kwargs):
        super().__init__(meta, **kwargs)
        self.base_capital = base_capital
        self.buy_cost = buy_cost
        self.sell_cost = sell_cost
        self.slippage = slippage

    def save(self, using=None, index=None, validate=True, **kwargs):
        self.meta.id = self.traderId
        return super().save(using, index, validate, **kwargs)

    @classmethod
    def generate_id(cls, id):
        # 保证id唯一
        account = Account.get(id=id, ignore=404)
        if account:
            i = id.rfind('_')
            if i == 0:
                id = "{}_{}".format(id, 1)
            else:
                count = int(id[i + 1:])
                id = "{}_{}".format(id, count)
            return Account.generate_id(id=id)
        else:
            return id

    class Meta:
        index = 'account'
        doc_type = 'doc'
        all = MetaField(enabled=False)

    def get_position(self, security_id):
        for position in self.positions:
            if position.securityId == security_id:
                return position
        return None

    def refresh(self):
        current = self.get(id=self.traderId)
        print(current)

    def update_position(self, security_id, amount_change, current_price, timestamp):
        current_position = None
        has_position = False
        for position in self.positions:
            if position.securityId == security_id:
                current_position = position
                has_position = True
        if not current_position:
            current_position = Position()

        # 买
        if amount_change > 0:
            # 不差钱
            need_money = (amount_change * current_price) * (1 + self.slippage + self.buy_cost)
            if self.cash >= need_money:
                self.cash -= need_money
                current_position.amount += amount_change
            else:
                raise Exception("not enough money")
        # 卖
        elif amount_change < 0:
            # 不差货
            if current_position.amount >= abs(amount_change):
                current_position.amount += amount_change
                self.cash += (amount_change * current_price) * (1 - self.slippage - self.sell_cost)
            else:
                raise Exception("not enough pos")

        if not has_position:
            self.positions.append(current_position)
        self.timestamp = timestamp
        self.save()


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
