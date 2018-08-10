# -*- coding: utf-8 -*-

# Scrapy settings for fospider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
import os

BOT_NAME = 'fooltrader'

SPIDER_MODULES = ['fooltrader.spiders']
NEWSPIDER_MODULE = 'fooltrader.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'fospider (+http://www.yourdomain.com)'

# Obey robots.txt rules
# ROBOTSTXT_OBEY = True

COMPRESSION_ENABLED = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'fospider.middlewares.MyCustomSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'fooltrader.middlewares.ForbiddenHandleMiddleware': 1000,
}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
# ITEM_PIPELINES = {
#    'fospider.pipelines.SomePipeline': 300,
# }

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 0.2
# Enable showing throttling stats for every response received:
AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# 把这个改为你的data目录的绝对路劲,方便在任何地方使用python
FOOLTRADER_STORE_PATH = os.environ.get('FOOLTRADER_STORE_PATH')
if not FOOLTRADER_STORE_PATH:
    FOOLTRADER_STORE_PATH = '/home/xuanqi/workspace/github/fooltrader/data'

STOCK_START_CODE = '000001'
STOCK_END_CODE = '666666'

US_STOCK_CODES = ['MSFT', 'AMZN', 'NVDA', 'SINA', 'AAPL']
# US_STOCK_CODES = ['MSFT']

AVAILABLE_TICK_DATE = '2004-10-8'
START_TICK_DATE = '2013-1-1'
FORCE_DOWNLOAD_SECURITY_LIST = False

DOWNLOAD_TXT_ENCODING = 'GB2312'

AUTO_KAFKA = False
KAFKA_HOST = 'localhost:9092'
KAFKA_PATH = '/home/xuanqi/software/kafka_2.11-0.11.0.1'
ZK_KAFKA_HOST = 'localhost:2181'

# http://www.delegate.org/delegate/
# 用于socks转http
DG_PATH = '/Users/xuanqi/software/delegate/DGROOT/bin/delegate'

SUPPORT_SOCKS2HTTP = False

g_socks_proxy_items = []
g_http_proxy_items = []
g_socks2http_proxy_items = {}

TIME_FORMAT_MICRO = "%Y%m%d %H%M%S.%f"

TIME_FORMAT_SEC = '%Y-%m-%d %H:%M:%S'

TIME_FORMAT_DAY = '%Y-%m-%d'

# ES_HOSTS = ['172.16.92.200:9200']
ES_HOSTS = ['localhost:9200']

# the action account settings
SMTP_HOST = 'smtpdm.aliyun.com'
SMTP_PORT = '80'

EMAIL_USER_NAME = ''

if not EMAIL_USER_NAME:
    EMAIL_USER_NAME = os.environ.get('EMAIL_USER_NAME')

EMAIL_PASSWORD = ''
if not EMAIL_PASSWORD:
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')

WEIXIN_APP_ID = ""
if not WEIXIN_APP_ID:
    WEIXIN_APP_ID = os.environ.get("WEIXIN_APP_ID")

WEIXIN_APP_SECRECT = ""
if not WEIXIN_APP_SECRECT:
    WEIXIN_APP_SECRECT = os.environ.get("WEIXIN_APP_SECRECT")

EOS_MONGODB_URL = ""

if not EOS_MONGODB_URL:
    EOS_MONGODB_URL = os.environ.get("EOS_MONGODB_URL")
