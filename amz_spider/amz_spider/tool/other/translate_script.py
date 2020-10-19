import os
import time
import json
import urllib
import random
import hashlib
import http.client
from amz_spider.tool.db.mysql_server import Mysql_server


class TranslateScript(object):
    def __init__(self, table, fromLang='auto', toLang='zh'):
        env_dist = os.environ
        self.table = table
        self.toLang = toLang
        self.fromLang = fromLang
        self.mysql = Mysql_server()
        self.cursor = self.mysql.get_cursor()
        self.appid = env_dist.get('baidufanyi_appid')  # 填写你的appid
        self.secretKey = env_dist.get('baidufanyi_secretKey')  # 填写你的密钥

    def translate(self, q='/'):
        httpClient = None
        toLang = self.toLang
        fromLang = self.fromLang
        myurl = '/api/trans/vip/translate'
        salt = random.randint(32768, 65536)
        sign = self.appid + str(q) + str(salt) + self.secretKey
        sign = hashlib.md5(sign.encode()).hexdigest()
        myurl = myurl + '?appid=' + self.appid + '&q=' + urllib.parse.quote(
            q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(
            salt) + '&sign=' + sign
        try:
            httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
            httpClient.request('GET', myurl)
            # response是HTTPResponse对象
            response = httpClient.getresponse()
            result_all = response.read().decode("utf-8")
            result = json.loads(result_all)
            return result.get('trans_result')[0].get('dst')
        except Exception as e:
            print(e)
        finally:
            if httpClient:
                httpClient.close()

    def get_data(self):
        select_sql = "select id, review_title, review_body from {} where state=0 limit 10".format(self.table)
        self.cursor.execute(select_sql)
        data = self.cursor.fetchall()
        for record in data:
            parmas = (record[0])
            update_sql = "update {} set state=1 where id=%s".format(self.table)
            self.cursor.execute(update_sql, parmas)
        self.mysql.conn.commit()
        return data

    def update_data(self, item):
        params = (item['translate_review_title'], item['translate_review_body'], item['id'])
        update_sql = "update {} set translate_review_title=%s, translate_review_body=%s, state=2 where id=%s".format(
            self.table)
        self.cursor.execute(update_sql, params)
        self.mysql.conn.commit()
        print('{}更新成功'.format(item['id']))

    def close_link(self):
        self.mysql.conn.close()

    def start(self):
        data = self.get_data()
        for record in data:
            translate_review_title = ''
            translate_review_body = ''
            if record[2]:
                translate_review_body = self.translate(q=record[2]) or ''
                time.sleep(2)
            if record[1]:
                translate_review_title = self.translate(q=record[1]) or ''
                time.sleep(1)
            item = {
                'id': record[0],
                'translate_review_title': translate_review_title,
                'translate_review_body': translate_review_body,
            }
            self.update_data(item)
        self.close_link()


if __name__ == '__main__':
    while True:
        t = TranslateScript(table='product_reviews', fromLang='auto', toLang='zh')
        t.start()
        print('------------')
