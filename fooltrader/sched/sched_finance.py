# -*- coding: utf-8 -*-

import logging

from apscheduler.schedulers.background import BackgroundScheduler

from fooltrader.connector import es_connector
from fooltrader.datamanager import process_crawl
from fooltrader.datamanager.china_stock_manager import crawl_finance_data
from fooltrader.spiders.chinastock.stock_forecast_spider import StockForecastSpider
from fooltrader.utils.utils import init_process_log

init_process_log('crawling_china_finance_data.log')

logger = logging.getLogger(__name__)

sched = BackgroundScheduler()


@sched.scheduled_job('cron', hour=18, minute=00)
def scheduled_job1():
    crawl_finance_data('000001', '666666')
    es_connector.finance_sheet_to_es()
    es_connector.finance_event_to_es(event_type='finance_report')


@sched.scheduled_job('cron', hour=18, minute=10)
def scheduled_job2():
    process_crawl(StockForecastSpider)
    es_connector.finance_event_to_es(event_type='finance_forecast')


if __name__ == '__main__':
    logger.info("start crawling finance data")

    crawl_finance_data('000001', '666666')
    process_crawl(StockForecastSpider)

    logger.info("shed crawling finance data")

    sched.start()

    logger.info("I would crawl finance data at 18:00")
    sched._thread.join()
