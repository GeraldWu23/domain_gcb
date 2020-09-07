#coding=utf-8

import sys
import os
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import scrapy
import redis
from scrapy.crawler import CrawlerProcess
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
from settings import REDIS_PORT
from scrapy.selector import Selector
from scrapy.settings import Settings
import settings as my_settings
import settings


POS_PROJECT = '~/'
sys.path.append(POS_PROJECT + '/domain_gcb/')
localPort = REDIS_PORT  # 10031 in server

import numpy as np
from scrapy_redis.spiders import RedisSpider
from items import DemoItem
from scrapy.utils.serialize import ScrapyJSONEncoder
DEFAULT_SERIALISER = ScrapyJSONEncoder().encode
from scrapy_redis.pipelines import *

np.set_printoptions(suppress=True)    # 用来修改时间格式，避免科学计数表示

class MySpider(RedisSpider):
    name = 'MySpider'
    redis_key = "MySpider:start_urls"

    def __init__(self, *args, **kwargs):
        super(MySpider, self).__init__(*args, **kwargs)
        # self.server = redis.Redis(host=settings.get('REDIS_HOST'), port=settings.get('REDIS_PORT'), db=0)  # port=6379 in pc, 10031 in server
        # self.serialise = DEFAULT_SERIALISER

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, errback=self.error_back)  # default encoding = 'utf-8'

    def parse(self, response):
        # with open(f'D:/PycharmProjects/response_showtest.txt', 'wb') as f:  # no encoding problem, perfectly written
        #     f.write(response.body)

        item = DemoItem()
        item['url'] = response.url
        item['html'] = str(response.body, encoding='utf-8')
        # serialised_item = self.serialise(item)
        # self.server.rpush("MySpider:items", serialised_item)
        # get score
        # hub or authority
        # item['content'] = ' '.join(response.xpath('//div/p/text()').extract())

        yield item

    def error_back(self, failure):
        self.logger.error(repr(failure))

        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.error(f'HttpError on {response.url}')

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)



if __name__ == '__main__':

    pass







