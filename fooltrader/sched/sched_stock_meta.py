# -*- coding: utf-8 -*-

import logging

from apscheduler.schedulers.background import BackgroundScheduler

from fooltrader.datamanager.china_stock_manager import crawl_stock_meta, craw_stock_category

logger = logging.getLogger(__name__)

sched = BackgroundScheduler()


@sched.scheduled_job('cron', hour=12, minute=00)
def scheduled_job1():
    crawl_stock_meta()


@sched.scheduled_job('cron', hour=12, minute=30)
def scheduled_job2():
    craw_stock_category()


sched.start()

logger.info("I would crawl stock meta at 12:00")
sched._thread.join()
