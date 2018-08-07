# -*- coding: utf-8 -*-
import logging
from multiprocessing import Process

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

logger = logging.getLogger(__name__)


def crawl(spider, setting):
    process = CrawlerProcess({**get_project_settings(), **setting})
    process.crawl(spider)
    process.start()


def process_crawl(spider, setting={}):
    p = Process(target=crawl, args=(spider, setting))
    p.start()
    # 爬虫假死
    max_run_time = 30
    p.join(max_run_time * 60)
    if p.is_alive():
        logger.warning("kill the spider:{} which has run {} minutes,".format(type(spider).__name__), max_run_time)
        p.terminate()
