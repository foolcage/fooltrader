# -*- coding: utf-8 -*-

import logging

from apscheduler.schedulers.background import BackgroundScheduler

from fooltrader.datamanager.china_stock_manager import crawl_stock_quote, crawl_index_quote
from fooltrader.utils.utils import init_process_log

init_process_log('crawling_china_stock_quote.log')

logger = logging.getLogger(__name__)

sched = BackgroundScheduler()


@sched.scheduled_job('cron', hour=17, minute=00)
def scheduled_job1():
    crawl_stock_quote('000001', '666666')


@sched.scheduled_job('cron', hour=18, minute=00)
def scheduled_job2():
    crawl_index_quote()


if __name__ == '__main__':
    logger.info("start crawling stock china stock quote")

    crawl_stock_quote('000001', '666666')
    crawl_index_quote()

    logger.info("shed crawling china stock quote")

    sched.start()

    logger.info("I would crawl china stock quote at 17:00 everyday")
    sched._thread.join()
