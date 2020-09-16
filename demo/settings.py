# -*- coding: utf-8 -*-

# Scrapy settings for demo project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html


BOT_NAME = 'demo'

SPIDER_MODULES = ['demo.spiders']
NEWSPIDER_MODULE = 'demo.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'demo (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)  多线程
CONCURRENT_REQUESTS = 1

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16
RETRY_TIMES = 1
DOWNLOAD_TIMEOUT = 60

# Disable cookies (enabled by default)
COOKIES_ENABLED = True  # 这里将COOKIES_ENABLED参数置为True，使根据cookies判断访问的站点不能发现爬虫轨迹，防止被ban

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'demo.middlewares.DemoSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    'demo.middlewares.DemoDownloaderMiddleware': 543,
# }

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'demo.pipelines.DemoPipeline': 300,
    'scrapy_redis.pipelines.RedisPipeline': 400,
}

# DOWNLOADER_MIDDLEWARES = {
#    'demo.monitor.statscol.StatcollectorMiddleware': 200,
# }


MYEXT_ENABLED=True      # 开启扩展
IDLE_NUMBER=50         # 配置空闲持续时间单位为 360个 ，一个时间单位为5s
EXTENSIONS= {
   'demo.extensions.RedisSpiderSmartIdleClosedExensions': 500,
}

#redis配置(下面有两种方式)
#方式一：没有密码
REDIS_HOST = 'localhost'  # localhost
REDIS_PORT = 10031  # 10031, 6379
#redis字符集设定
REDIS_ENCODING = 'utf-8'


# 连接管道
# MONGODB 主机名
MONGODB_HOST =  'localhost' # localhost
# MONGODB 端口号
MONGODB_PORT = '27017'  # 11044 in server, 27017 in pc
# 数据库名称
MONGODB_DBNAME = "cailiao"
# 存放数据的表名称
MONGODB_SHEETNAME = "url_info"

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 16  # set to the same value as CONCURRENT_REQUEST
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'


SCHEDULER = "scrapy_redis.scheduler.Scheduler"
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderPriorityQueue"
SCHEDULER_PERSIST = True


# 深度优先 or广度优先
'''
    _PRIORITY 定义深度or广度，
    _lIMIT 定义爬取深度
'''
DEPTH_PRIORITY = 1
DEPTH_LIMIT = 1
#SCHEDULER_DISK_QUEUE = 'scrapy.squeues.PickleFifoDiskQueue'
#SCHEDULER_MEMORY_QUEUE = 'scrapy.squeues.FifoMemoryQueue'


USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'

# DEDUPFILTER USING BLOOMFILTER
FILTER_URL = None
FILTER_HOST = MONGODB_HOST
FILTER_PORT = REDIS_PORT  # 10031, 6379
FILTER_DB = 0
