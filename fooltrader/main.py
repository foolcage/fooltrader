from apscheduler.schedulers.background import BackgroundScheduler

from fooltrader.datamanager.datamanager import crawl_stock_data

sched = BackgroundScheduler()


# 每天下午5:00抓取数据
@sched.scheduled_job('cron', hour=18, minute=1)
def scheduled_job():
    crawl_stock_data()


sched.start()

sched._thread.join()
