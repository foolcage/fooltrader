# -*- coding: utf-8 -*-

from datetime import datetime

from elasticsearch_dsl import connections
from kafka import KafkaProducer

from fooltrader.api.computing import *
from fooltrader.api.event import *
from fooltrader.api.fundamental import *
from fooltrader.api.technical import *
from fooltrader.api.technical import get_security_list
from fooltrader.contract.data_contract import EXCHANGE_LIST_COL
from fooltrader.contract.files_contract import get_finance_dir, get_tick_dir, get_event_dir, get_kdata_dir, \
    get_exchange_dir, get_exchange_cache_dir
from fooltrader.settings import FOOLTRADER_STORE_PATH, ES_HOSTS, KAFKA_HOST


def init_log():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # fh = logging.FileHandler('fooltrader.log')
    # fh.setLevel(logging.INFO)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        "%(levelname)s  %(threadName)s  %(asctime)s  %(name)s:%(lineno)s  %(funcName)s  %(message)s")
    # fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to the logger
    # root_logger.addHandler(fh)
    root_logger.addHandler(ch)


def mkdir_for_stock(item):
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
    if not os.path.exists(FOOLTRADER_STORE_PATH):
        print("{} is a wrong path")
        print("please set env FOOLTRADER_STORE_PATH to working path or set it in settings.py")
    else:
        # 初始化股票文件夹
        for _, item in get_security_list(exchanges=EXCHANGE_LIST_COL).iterrows():
            mkdir_for_stock(item)

        # 初始化指数文件夹
        for _, item in get_security_list(security_type='index', exchanges=['sh', 'sz', 'nasdaq']).iterrows():
            kdata_dir = get_kdata_dir(item)
            if not os.path.exists(kdata_dir):
                os.makedirs(kdata_dir)
        # 初始化期货文件夹
        for exchange in ['shfe', 'dce', 'zce']:
            exchange_cache_dir = get_exchange_cache_dir(security_type='future', exchange=exchange)
            if not os.path.exists(exchange_cache_dir):
                os.makedirs(exchange_cache_dir)

            exchange_cache_dir = get_exchange_cache_dir(security_type='future', exchange='shfe',
                                                        the_year=datetime.datetime.today().year,
                                                        data_type="day_kdata")
            if not os.path.exists(exchange_cache_dir):
                os.makedirs(exchange_cache_dir)

            exchange_dir = get_exchange_dir(security_type='future', exchange=exchange)
            if not os.path.exists(exchange_dir):
                os.makedirs(exchange_dir)


pd.set_option('expand_frame_repr', False)

init_log()

init_env()

logger = logging.getLogger(__name__)

try:
    es_client = connections.create_connection(hosts=ES_HOSTS)
except Exception as e:
    logger.exception(e)

try:
    kafka_producer = KafkaProducer(bootstrap_servers=KAFKA_HOST)
except Exception as e:
    logger.exception(e)
