# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from amz_spider.tool.db.mysql_server import Mysql_server
import time
import pymongo
import pymysql
import json


class AmzSpiderPipeline(object):
    def process_item(self, item, spider):
        return item


class AmzReviewsPipeline(object):
    def open_spider(self, spider):
        self.mysql_server = Mysql_server()

    def process_item(self, item, spider):
        timestamp = int(int(time.time()) / 86400) * 86400
        cursor = self.mysql_server.get_cursor()
        params = (item['reviewID'], item['review_time'], item['review_raiting'],
                  item['helpful_num'], item['review_title'], item['review_body'],
                  item['is_VP'], item['asin'], item['profileID'], item['country'], timestamp)
        sql = """insert into product_reviews (reviewID, review_time, review_raiting, helpful_num,
                             review_title, review_body, is_VP, asin, profileID, country, timestamp)
                     values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)"""
        cursor.execute(sql, params)
        self.mysql_server.conn.commit()
        return item

    def close_spider(self, spider):
        self.mysql_server.conn.close()


class AmzProductPipeline(object):
    def open_spider(self, spider):
        self.mysql_server = Mysql_server()
        self.client = pymongo.MongoClient('127.0.0.1', 27017, maxPoolSize=100)
        self.db = self.client.amazon
        self.collection = self.db.detail_info

    def process_item(self, item, spider):
        timestamp = int(time.time())
        cursor = self.mysql_server.get_cursor()
        params = (item['asin'], item['seller_type'], item['seller_num'],
                  item['brand'], item['price'], item['listing_rating'],
                  item['ratings'], item['stock_status'], item['QA_num'], timestamp, item['sellerName'],
                  item['sellerID'], item['country'], item['reviews'], item['actual_reviews'], item['critical'],
                  item['vp_num'], item['product_style'], item["avg30"])
        detail_sql = """insert into product_detail (id, asin, seller_type, seller_num, brand,
                             price, listing_rating, ratings, stock_status, QA_num, timestamp,
                              sellerName, sellerID, country, reviews, actual_reviews, critical, vp_num, product_style, avg30)
                     values (0, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(detail_sql, params)
        self.mysql_server.conn.commit()
        rank_sql = f"""insert into product_rankinfo (id, asin, categoryID,
                       category, `rank`, timestamp, country) values (0, %s, %s, %s, %s, %s, %s)"""
        rank_list = item['rank_list']['ranks']
        for data in rank_list:
            params = (item['asin'], data['catId'], data['name'], int(data['rank']), timestamp, item['country'])
            cursor.execute(rank_sql, params)
            self.mysql_server.conn.commit()
        target_data = {"asin": item['asin'], "frequently_bought_asins": item['frequently_bought_asins'],
                       "title": item['title'], "img_list": item['img_list'], "variant_list": item['variant_list'],
                       "parentasin": item['parentasin'], "vari_num": item['vari_num'],
                       "feature": item['feature'], "product_info": json.dumps(item['product_info']),
                       "product_descript": json.dumps(item['product_descript']),
                       "compare_info": json.dumps(item['compare_info']),
                       "other_info": item['other_info'], 'country': item['country'], "timestamp": timestamp}
        str_data = json.dumps(target_data, ensure_ascii=False)
        target_data = json.loads(str_data)
        self.collection.insert_one(target_data)
        return item

    def close_spider(self, spider):
        self.mysql_server.conn.close()
        self.client.close()


class AmzKeywordsPipeline(object):
    def open_spider(self, spider):
        self.mysql_server = Mysql_server()

    def process_item(self, item, spider):
        timestamp = int(time.time())
        cursor = self.mysql_server.get_cursor()
        table_name = item['country'] + '_asins'
        params = (item['asin'], item['pageNum'], item['positionNum'],
                  item['keyword'], timestamp, item['ad'])
        sql = f"""insert into {table_name} (id, asin, pageNum, positionNum, keyword, timestamp,state, ad)
                     values (0, %s, %s, %s, %s, %s, 0, %s)"""
        # print(sql,params)
        cursor.execute(sql, params)
        self.mysql_server.conn.commit()
        return item

    def close_spider(self, spider):
        self.mysql_server.conn.close()


class AmzSellerPipeline(object):
    def open_spider(self, spider):
        self.mysql_server = Mysql_server()

    def process_item(self, item, spider):
        item = item['data']
        timestamp = int(time.time())
        cursor = self.mysql_server.get_cursor()
        params = (item['sellerID'], item['negative_lifetime'], item['count_lifetime'],
                  timestamp, item['country'])
        sql = f"""insert into seller_info (id, sellerID, negative_lifetime, count_lifetime, timestamp,country)
                     values (0, %s, %s, %s, %s, %s)"""
        # print(sql,params)
        cursor.execute(sql, params)
        params = (item['sellerID'],)
        sql = f"""update product_detail set state=2 where sellerID=%s"""
        cursor.execute(sql, params)
        self.mysql_server.conn.commit()
        return item

    def close_spider(self, spider):
        self.mysql_server.conn.close()


class SellerspritePipeline(object):
    def open_spider(self, spider):
        self.mysql_server = Mysql_server()

    def process_item(self, item, spider):
        cursor = self.mysql_server.get_cursor()
        for sale_data in item['total_dict'].items():
            # m_add:只保存当月的数据 2020-10-07
            if sale_data[0] != '2020-10':
                continue
            params = (item['asin'], sale_data[-1], sale_data[0])
            sql = f"""	insert into product_sales (id, asin, sales, date) values 
                        (0, %s,%s,%s) 
                        on duplicate key update sales=values(sales)"""
            cursor.execute(sql, params)
        for rankdata in item['rankHistory'].items():
            params = (item['asin'], rankdata[-1], rankdata[0])
            sql = f"""INSERT into product_sales (id, asin, sales, date) values (0, %s, %s, %s) ON DUPLICATE KEY UPDATE sales=values(%s)"""
            #
            sql = f"""	insert into product_rank (id, asin, `rank`, date) values
                        (0, %s,%s,%s)
                        on duplicate key update `rank`=values(`rank`)"""
            # print(sql % params, '======================')
            cursor.execute(sql, params)
        params = (item['asin'],)
        sql = f"""update {item['table_name']} set state=4 where asin=%s"""
        cursor.execute(sql, params)
        self.mysql_server.conn.commit()
        return item

    def close_spider(self, spider):
        self.mysql_server.conn.close()


class AmzProfilePipeline(object):
    def open_spider(self, spider):
        self.mysql_server = Mysql_server()

    def process_item(self, item, spider):
        cursor = self.mysql_server.get_cursor()
        params = (item['profileID'],)
        sql = """update product_toplistreviews set state=2 where profileID=%s"""
        cursor.execute(sql, params)
        params = (item['profileID'], item['helpfulVotes'], item['reviews'], item['location'], item['occupation'],
                  item['facebook'], item['twitter'], item['instagram'], item['youtube'], item['country'], item['rank'],
                  item['name'])
        sql = """insert into profile_info (id, profileID, helpfulVotes, reviews, location, occupation, facebook, twitter,
                instagram, youtube, country, `rank`, name) values(0, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) on duplicate key update reviews=values(reviews), rank=values(rank)"""
        cursor.execute(sql, params)
        self.mysql_server.conn.commit()
        return item

    def close_spider(self, spider):
        self.mysql_server.conn.close()


class AmzTopReviewsPipeline(object):
    def open_spider(self, spider):
        self.mysql_server = Mysql_server()

    def process_item(self, item, spider):
        timestamp = int(int(time.time()) / 86400) * 86400
        cursor = self.mysql_server.get_cursor()
        params = (item['profileID'],)
        sql = """update product_reviews set state=2 where profileID=%s"""
        cursor.execute(sql, params)
        params = (item['reviewID'], item['review_time'], item['review_raiting'],
                  item['helpful_num'], item['review_title'], item['review_body'],
                  item['is_VP'], item['asin'], item['profileID'], item['country'], timestamp)
        sql = """insert into product_topreviews (reviewID, review_time, review_raiting, helpful_num,
                             review_title, review_body, is_VP, asin, profileID, country, timestamp)
                     values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)"""
        cursor.execute(sql, params)
        self.mysql_server.conn.commit()
        return item

    def close_spider(self, spider):
        self.mysql_server.conn.close()


class AmzToplistReviewsPipeline(object):
    def open_spider(self, spider):
        self.mysql_server = Mysql_server()

    def process_item(self, item, spider):
        timestamp = int(int(time.time()) / 86400) * 86400
        cursor = self.mysql_server.get_cursor()
        params = (item['profileID'], item['country'], timestamp)
        sql = """insert ignore into product_toplistreviews (id, profileID, country, timestamp)
                     values (0, %s, %s, %s)"""
        cursor.execute(sql, params)
        self.mysql_server.conn.commit()
        return item

    def close_spider(self, spider):
        self.mysql_server.conn.close()


class AmzbsrPipeline(object):
    def open_spider(self, spider):
        self.mysql_server = Mysql_server()

    def process_item(self, item, spider):
        timestamp = int(int(time.time()) / 86400 / 30) * 86400 * 30
        cursor = self.mysql_server.get_cursor()
        if item['flag'] == 1:
            params = (item['category_id'], item['category_name'], item['category_id'] + f'_{timestamp}', item['level'],
                      item['parent_id'], 0, item['bsr_url'], item['country'])
            sql = """insert into amz_category (id, category_id, category_name, node_name, uid, level, parent_id, state, bsr_url, country)
                         values (0, %s, '',%s, %s, %s, %s, %s, %s, %s)"""
            # params = (item['category_name'], item['category_id'], item['country'])
            # sql = """update amz_category set node_name=%s where category_id=%s and country=%s"""
            # print('----')
        elif item['flag'] == 0:
            return
            timestamp = int(time.time())
            table_name = item['data']['country'] + '_asins'
            params = (item['data']['asin'], 1, item['data']['rank'],
                      'bsr_' + item['data']['categoryId'], timestamp, 0)
            sql = f"""insert into {table_name} (id, asin, pageNum, positionNum, keyword, timestamp,state, ad)
                         values (0, %s, %s, %s, %s, %s, 0, %s)"""
        elif item['flag'] == 2:
            print(f'======{item["category_name"]}=======')
            params = (item['category_name'], item['category_id'], item['country'])
            sql = """update amz_category set category_name=%s where category_id=%s and country=%s"""
        # try:
        cursor.execute(sql, params)
        self.mysql_server.conn.commit()
        # except:
        #     pass
        return item

    def close_spider(self, spider):
        self.mysql_server.conn.close()


class SorftimePipeline(object):
    def open_spider(self, spider):
        self.mysql_server = Mysql_server()

    def process_item(self, item, spider):
        cursor = self.mysql_server.get_cursor()
        params = (
            item['asin'], item['category_name'], item['rank'], item['bsr_url'], item['category_id'], item['sales'],
            item['country'], item['brand'], item['SalePrice'], item['product_url'], item['level'])
        sql = f"""insert into sorftime_sales_other (id, asin, category_name, `rank`, bsr_url, category_id, sales, country,
                              brand,SalePrice,product_url,level
         ) values(0, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) on duplicate key update sales=values(sales)"""
        cursor.execute(sql, params)
        # timestamp = int(time.time())
        # table_name = item['country'] + '_asins'
        # params = (item['asin'], 1, item['rank'],
        # 'bsr_' + item['category_id'], timestamp, 0)
        # sql = f"""insert into {table_name} (id, asin, pageNum, positionNum, keyword, timestamp,state, ad)
        #            values (0, %s, %s, %s, %s, %s, 0, %s)"""
        # cursor.execute(sql, params)
        self.mysql_server.conn.commit()
        return item

    def close_spider(self, spider):
        self.mysql_server.conn.close()
