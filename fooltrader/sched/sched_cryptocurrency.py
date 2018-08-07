# -*- coding: utf-8 -*-

import logging

from apscheduler.schedulers.background import BackgroundScheduler

from fooltrader.consts import CRYPTOCURRENCY_EXCHANGES
from fooltrader.datasource.ccxt_wrapper import init_markets, fetch_kdata
from fooltrader.utils.utils import init_process_log

init_process_log('crawling_cryptocurrency_data.log')

logger = logging.getLogger(__name__)

sched = BackgroundScheduler()


@sched.scheduled_job('cron', hour=00, minute=00)
def scheduled_job1():
    init_markets()


@sched.scheduled_job('cron', hour=00, minute=30)
def scheduled_job2():
    for item in CRYPTOCURRENCY_EXCHANGES:
        fetch_kdata(item)


if __name__ == '__main__':
    init_markets()
    for item in CRYPTOCURRENCY_EXCHANGES:
        fetch_kdata(item)

    sched.start()

    logger.info("I would crawl cryptocurrency at 00:00")
    sched._thread.join()
