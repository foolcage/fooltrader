import logging
import os

from fooltrader import settings
from fooltrader.api.quote import get_security_list
from fooltrader.contract.files_contract import get_finance_dir, get_tick_dir, get_event_dir, get_kdata_dir


def init_log():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # fh = logging.FileHandler('fooltrader.log')
    # fh.setLevel(logging.INFO)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # create formatter and add it to the handlers
    formatter = logging.Formatter("%(levelname) -10s %(asctime)s %(module)s:%(lineno)s %(funcName)s %(message)s")
    # fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to the logger
    # root_logger.addHandler(fh)
    root_logger.addHandler(ch)


def mkdir_for_security(item):
    finance_dir = get_finance_dir(item)
    if not os.path.exists(finance_dir):
        os.makedirs(finance_dir)

    tick_dir = get_tick_dir(item)
    if not os.path.exists(tick_dir):
        os.makedirs(tick_dir)

    event_dir = get_event_dir(item)
    if not os.path.exists(event_dir):
        os.makedirs(event_dir)

    bfq_kdata_dir = get_kdata_dir(item, 'bfq')
    if not os.path.exists(bfq_kdata_dir):
        os.makedirs(bfq_kdata_dir)

    hfq_kdata_dir = get_kdata_dir(item, 'hfq')
    if not os.path.exists(hfq_kdata_dir):
        os.makedirs(hfq_kdata_dir)


def init_env():
    if not os.path.exists(settings.FILES_STORE):
        os.makedirs(settings.FILES_STORE)
    # 初始化股票文件夹
    for _, item in get_security_list().iterrows():
        mkdir_for_security(item)

    # 初始化指数文件夹
    for _, item in get_security_list(security_type='index').iterrows():
        kdata_dir = get_kdata_dir(item)
        if not os.path.exists(kdata_dir):
            os.makedirs(kdata_dir)


init_log()
init_env()
