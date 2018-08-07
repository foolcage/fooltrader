# -*- coding: utf-8 -*-

import logging

from apscheduler.schedulers.background import BackgroundScheduler

from fooltrader.connector import es_connector
from fooltrader.datamanager.china_stock_manager import crawl_stock_meta, craw_stock_category
from fooltrader.utils.utils import init_process_log

init_process_log('crawling_stock_meta.log')

logger = logging.getLogger(__name__)

sched = BackgroundScheduler()


@sched.scheduled_job('cron', hour=00, minute=00)
def scheduled_job1():
    crawl_stock_meta()


@sched.scheduled_job('cron', hour=00, minute=10)
def scheduled_job2():
    craw_stock_category()
    es_connector.security_meta_to_es()


if __name__ == '__main__':
    logger.info("start crawling stock meta")

    crawl_stock_meta()
    craw_stock_category()

    logger.info("shed crawling stock meta")

    sched.start()

    logger.info("I would crawl stock meta at 00:00 everyday")
    sched._thread.join()
