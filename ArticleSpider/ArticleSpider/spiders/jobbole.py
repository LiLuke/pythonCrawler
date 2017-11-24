# -*- coding: utf-8 -*-
import scrapy
import re
import datetime
from scrapy.http import Request
from urllib import parse
from ArticleSpider.items import JobBoleArticleItem, ArticleItemLoader
from ArticleSpider.utils.common import get_md5


class JobboleSpider(scrapy.Spider):
    name = "jobbole"
    allowed_domains = ["blog.jobbole.com"]
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """
        1.获取文章列表页中的文章url 交给解析函数进行具体字段的解析
        2.获取下一页的url并交给scrapy进行下载 下载完成交给parse
        :param response:
        :return:
        """
        # 解析列表页所有的文章url
        post_urls = response.css("#archive .floated-thumb .post-thumb a")
        for post_note in post_urls:
            # parse函数拼接相对路径的url
            # 利用meta对Request 进行传值
            post_url = post_note.css("::attr(href)").extract_first('')
            post_url = parse.urljoin(response.url, post_url)
            image_url = post_note.css("img::attr(src)").extract_first('')
            image_url = parse.urljoin(response.url, image_url)
            yield Request(url=post_url, meta={"front_image_url": image_url}, callback=self.parse_detail)

        # 提取下一页
        next_url = response.css(".next.page-numbers::attr(href)").extract_first()
        if next_url:
            yield Request(url=next_url, callback=self.parse)

    @staticmethod
    def parse_detail(response):
        # 通过ItemLoader 加载item
        front_image_url = response.meta.get("front_image_url", "")
        item_loader = ArticleItemLoader(item=JobBoleArticleItem(), response=response)
        item_loader.add_css("title", ".entry-header h1::text")
        item_loader.add_css("create_date", "p.entry-meta-hide-on-mobile::text")
        item_loader.add_css("content", "div.entry")
        item_loader.add_css("vote_nums", ".vote-post-up h10::text")
        item_loader.add_css("comment_nums", ".btn-bluet-bigger.href-style.hide-on-480::text")
        item_loader.add_css("fa_nums", ".btn-bluet-bigger.href-style.bookmark-btn.register-user-only::text")
        item_loader.add_css("tags", ".entry-meta-hide-on-mobile a::text")

        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_value("front_image_url", [front_image_url])

        article_data = item_loader.load_item()
        yield article_data
