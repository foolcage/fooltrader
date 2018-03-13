# -*- coding: utf-8 -*-

import logging

from apscheduler.schedulers.background import BackgroundScheduler

from fooltrader.datamanager.datamanager import crawl_stock_quote

logger = logging.getLogger(__name__)

sched = BackgroundScheduler()


# 每天下午5:00抓取数据
@sched.scheduled_job('cron', hour=17, minute=10)
def scheduled_job1():
    crawl_stock_quote('000001', '002999')

@sched.scheduled_job('cron', hour=17, minute=20)
def scheduled_job2():
    crawl_stock_quote('300000', '300999')

@sched.scheduled_job('cron', hour=17, minute=30)
def scheduled_job3():
    crawl_stock_quote('600000', '666666')

sched.start()

logger.info("I would crawl the data at 17:10")
sched._thread.join()
