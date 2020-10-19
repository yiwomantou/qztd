# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from zol.mysql_server import Mysql_server


class SeriesPipeline:
    def open_spider(self, spider):
        self.mysql_server = Mysql_server()

    def process_item(self, item, spider):
        cursor = self.mysql_server.get_cursor()
        params = (item['brand_name'], item['brand_url'], item['series_name'], item['series_url'])
        sql = f"""insert into series (id, brand_name, brand_url, series_name, series_url) values(0, %s, %s, %s, %s)"""
        cursor.execute(sql, params)
        self.mysql_server.conn.commit()
        print('{}写入成功'.format(item['series_name']))
        return item

    def close_spider(self, spider):
        self.mysql_server.conn.close()


class ModelPipeline:
    def open_spider(self, spider):
        self.mysql_server = Mysql_server()

    def process_item(self, item, spider):
        cursor = self.mysql_server.get_cursor()
        params = (
            item['product_name'], item['product_url'], item['product_data_interface'], item['product_video_interface'],
            item['product_audio_interface'], item['product_other_interface'], item['product_card_reader'],
            item['product_series_url'], item['conf_url'])
        sql = f"""insert into product_model (id, product_name, product_url, product_data_interface, 
                product_video_interface, product_audio_interface, product_other_interface, product_card_reader, 
                product_series_url, conf_url) values(0, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(sql, params)

        update_sql = f"""update series set state=2 where series_url=%s"""
        cursor.execute(update_sql, (item['product_series_url'],))
        self.mysql_server.conn.commit()
        print('{}写入成功'.format(item['product_name']))
        return item

    def close_spider(self, spider):
        self.mysql_server.conn.close()
