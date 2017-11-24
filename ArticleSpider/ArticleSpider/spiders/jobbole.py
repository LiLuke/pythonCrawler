# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
from urllib import parse
from scrapy.loader import ItemLoader
from ArticleSpider.items import JobBoleArticleItem
from ArticleSpider.utils.common import get_md5
import datetime


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
        # 通过css选择器提取字段
        article_data = JobBoleArticleItem()
        # 封面图
        front_image_url = response.meta.get("front_image_url", "")
        # 标题
        title = response.css('.entry-header h1::text').extract_first().strip()
        # 发布日期
        date = response.css("p.entry-meta-hide-on-mobile::text").extract_first('').strip().replace("·", "").strip()
        # 文章内容
        content = response.css("div.entry").extract_first('')
        # tags
        tag_list = response.css('.entry-meta-hide-on-mobile a::text').extract()
        tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        tags = ",".join(tag_list)
        # 评论数
        comment_nums = response.css(".btn-bluet-bigger.href-style.hide-on-480::text").extract_first('')
        match_re = re.match(".*(\d+).*", comment_nums)
        if match_re:
            comment_nums = int(match_re.group(1))
        else:
            comment_nums = 0
        # 收藏数
        fa_nums = response.css(".btn-bluet-bigger.href-style.bookmark-btn.register-user-only::text").extract_first()
        match_re = re.match(".*(\d+).*", fa_nums)
        if match_re:
            fa_nums = int(match_re.group(1))
        else:
            fa_nums = 0
        # 点赞数
        vote_nums = response.css(".vote-post-up h10::text").extract_first()
        match_re = re.match(".*(\d+).*", vote_nums)
        if match_re:
            vote_nums = int(match_re.group(1))
        else:
            vote_nums = 0

        try:
            date = datetime.datetime.strptime(date,"%Y/%m/%d").date()
        except Exception as e:
            date = datetime.datetime.now().date()
        article_data["title"] = title
        article_data["url"] = response.url
        article_data["url_object_id"] = get_md5(response.url)
        article_data["create_date"] = date
        article_data["front_image_url"] = [front_image_url]
        article_data["content"] = content
        article_data["vote_nums"] = vote_nums
        article_data["comment_nums"] = comment_nums
        article_data["fa_nums"] = fa_nums
        article_data["tags"] = tags

        # 通过ItemLoader 加载item
        item_loader = ItemLoader(item=JobBoleArticleItem(), response=response)
        item_loader.add_css("title", ".entry-header h1::text")
        item_loader.add_css("create_date", "p.entry-meta-hide-on-mobile::text")
        item_loader.add_css("content", "div.entry")
        item_loader.add_css("vote_nums", ".btn-bluet-bigger.href-style.hide-on-480::text")
        item_loader.add_css("comment_nums", ".btn-bluet-bigger.href-style.hide-on-480::text")
        item_loader.add_css("fa_nums", ".btn-bluet-bigger.href-style.bookmark-btn.register-user-only::text")
        item_loader.add_css("tags", ".entry-meta-hide-on-mobile a::text")

        item_loader.add_value("url", response.rul)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_value("front_image_url", [front_image_url])

        yield article_data
