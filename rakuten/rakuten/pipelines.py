# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from rakuten.db_server import Mysql_server


class ReviewsPipeline:
    def open_spider(self, spider):
        self.mysql_server = Mysql_server()

    def process_item(self, item, spider):
        cursor = self.mysql_server.get_cursor()
        params = (item['product_url'], item['review_url'], item['review_title'], item['review_body'],
                  item['review_time'], item['review_raiting'], item['critic_url'],)
        sql = f"""insert into reviews (id, product_url, review_url, review_title, review_body, review_time, 
                    review_raiting, critic_url) values(0, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(sql, params)
        self.mysql_server.conn.commit()
        print('{}写入成功'.format(item['review_title']))

    def close_spider(self, spider):
        self.mysql_server.close()


class CriticsPipeline:
    def open_spider(self, spider):
        self.mysql_server = Mysql_server()

    def process_item(self, item, spider):
        cursor = self.mysql_server.get_cursor()
        params = (item['critic_id'], item['critic_url'], item['age'], item['sex'], item['product_review'],
                  item['store_reviews'], item['product_bad_review'],)
        sql = f"""insert into critics (id, critic_id, critic_url, age, sex, product_review, store_reviews, 
                    product_bad_review) values(0, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(sql, params)
        self.mysql_server.conn.commit()

        update_sql = f"""update reviews set state=4 where id=%s"""
        cursor.execute(update_sql, (item['id'],))
        self.mysql_server.conn.commit()
        print('{}写入成功'.format(item['critic_url']))

    def close_spider(self, spider):
        self.mysql_server.close()


class ShopReviewsPipeline:
    def open_spider(self, spider):
        self.mysql_server = Mysql_server()

    def process_item(self, item, spider):
        cursor = self.mysql_server.get_cursor()
        params = (item['review_type'], item['product_name'], item['product_id'], item['review_detail_url'],
                  item['review_raiting'], item['review_time'], item['review_title'], item['review_body'],)
        sql = f"""insert into shop_reviews (id, review_type, product_name, product_id, review_detail_url, 
                    review_raiting, review_time, review_title, review_body) values(0, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(sql, params)
        self.mysql_server.conn.commit()
        print('{}写入成功'.format(item['review_type']))

    def close_spider(self, spider):
        self.mysql_server.close()
