# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class JobBoleArticleItem(scrapy.Item):
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field()
    image_file_path = scrapy.Field()
    title = scrapy.Field()
    create_date = scrapy.Field()
    content = scrapy.Field()
    tags = scrapy.Field()
    comment_nums = scrapy.Field()
    fa_nums = scrapy.Field()
    vote_nums = scrapy.Field()
