import logging

from apscheduler.schedulers.background import BackgroundScheduler

from fooltrader.datamanager.datamanager import crawl_stock_data

logger = logging.getLogger(__name__)

sched = BackgroundScheduler()


@sched.scheduled_job('cron', hour=17, minute=00)
def scheduled_job1():
    crawl_stock_data('000001', '002999')


@sched.scheduled_job('cron', hour=17, minute=20)
def scheduled_job2():
    crawl_stock_data('300000', '300999')


@sched.scheduled_job('cron', hour=17, minute=40)
def scheduled_job3():
    crawl_stock_data('600000', '666666')


sched.start()

logger.info("I would crawl quote data at 17:00")
sched._thread.join()
