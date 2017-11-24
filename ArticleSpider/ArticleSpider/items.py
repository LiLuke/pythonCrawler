# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import datetime
import re
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from scrapy.loader import ItemLoader

class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def add_jobbole(value):
    pass


def date_convert(value):
    try:
        value = datetime.datetime.strptime(value, "%Y/%m/%d").date()
    except Exception as e:
        value = datetime.datetime.now().date()
    return value


def get_nums(value):
    match_re = re.match(".*(\d+).*", value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0
    return nums


class ArticleItemLoader(ItemLoader):
    # 自定义ItemLoader
    default_output_processor = TakeFirst()


def remove_comment_tags(value):
    """
    去掉tags中提取的评论，
    :param value:
    :return:
    """
    if "评论" in value:
        return ""
    else:
        return value


def return_value(value):
    return value


class JobBoleArticleItem(scrapy.Item):
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        output_processor=return_value
    )
    image_file_path = scrapy.Field()
    title = scrapy.Field()
    create_date = scrapy.Field(
        input_processor=MapCompose(date_convert)
    )
    content = scrapy.Field()
    tags = scrapy.Field(
        input_processor=MapCompose(remove_comment_tags),
        output_processor=Join(",")
    )
    comment_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    fa_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    vote_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
