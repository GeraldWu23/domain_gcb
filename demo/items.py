# -*- coding: utf-8 -*-

import scrapy


class DemoItem(scrapy.Item):
    html = scrapy.Field()  # 页面 html
    # content = scrapy.Field()  # 页面 content
    url = scrapy.Field()  # 页面链接




