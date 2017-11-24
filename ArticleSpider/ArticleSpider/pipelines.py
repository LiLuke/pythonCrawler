# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
import MySQLdb
import MySQLdb.cursors

from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonWithEncodingPipeline(object):
    def __init__(self):
        self.file = codecs.open("article.json", 'w', encoding="utf-8")

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.close()


class JsonItemExporterPipeline(object):
    def __init__(self):
        self.file = codecs.open("article.json", 'wb')
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class MysqlPipeline(object):
    # 采用同步的机制写入mysql
    def __init__(self):
        self.conn = MySQLdb.connect(host='127.0.0.1', user='root', password='sa', database='article_spider', charset='utf8')
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
        INSERT INTO `article_spider`.`article`
                    ( `url`,`url_object_id`,`front_image_url`,`image_file_path`,`title`,
                    `content`,`tags`,`comment_nums`,`fa_nums`,`vote_nums`)
                    VALUES
                    (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) 
        """
        self.cursor.execute(insert_sql, (item['url'], item['url_object_id'], item['front_image_url'], item['image_file_path'], item['title'], item['content'], item['tags'], int(item['comment_nums']), int(item['fa_nums']), int(item['vote_nums'])))
        self.conn.commit()
        pass


class MysqlTwistedPipeline(object):
    # 采用异步的方式写入数据
    def __init__(self, db_pool):
        self.db_pool = db_pool

    @classmethod
    def from_settings(cls, settings):
        db_params = dict(
            host=settings["MYSQL_HOST"],
            database=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            password=settings["MYSQL_PASSWORD"],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True
        )
        db_pool = adbapi.ConnectionPool("MySQLdb", **db_params)

        return cls(db_pool)

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行
        query = self.db_pool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error)

    @staticmethod
    def handle_error(failure, ):
        print(failure)

    @staticmethod
    def do_insert(cursor, item):
        # 执行具体的插入操作
        insert_sql = """
                INSERT INTO `article_spider`.`article`
                            ( `url`,`url_object_id`,`front_image_url`,`image_file_path`,`title`,
                            `content`,`tags`,`comment_nums`,`fa_nums`,`vote_nums`)
                            VALUES
                            (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) 
                """
        cursor.execute(insert_sql, (item['url'], item['url_object_id'], item['front_image_url'],
                                    item['image_file_path'], item['title'], item['content'], item['tags'],
                                    int(item['comment_nums']), int(item['fa_nums']), int(item['vote_nums'])))
        pass


class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        for ok, value in results:
            image_file_path = value["path"]
        item["image_file_path"] = image_file_path
        return item
