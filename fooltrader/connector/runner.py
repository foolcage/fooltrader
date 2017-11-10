from fooltrader.api.hq import get_security_list
from fooltrader.utils.utils import init_trading_dates


def init_all_traing_dates():
    for _, item in get_security_list().iterrows():
        init_trading_dates(item)


if __name__ == '__main__':
    init_trading_dates()
