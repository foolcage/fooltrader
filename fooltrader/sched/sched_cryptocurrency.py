# -*- coding: utf-8 -*-

import logging

from apscheduler.schedulers.background import BackgroundScheduler

from fooltrader.consts import CRYPTOCURRENCY_EXCHANGES
from fooltrader.datasource.ccxt_wrapper import init_markets, fetch_kdata

logger = logging.getLogger(__name__)

sched = BackgroundScheduler()


@sched.scheduled_job('cron', hour=10, minute=00)
def scheduled_job1():
    init_markets()


@sched.scheduled_job('cron', hour=11, minute=00)
def scheduled_job2():
    for item in CRYPTOCURRENCY_EXCHANGES:
        fetch_kdata(item)


sched.start()

logger.info("I would crawl stock meta at 12:00")
sched._thread.join()
