import pymysql
import pymongo
from dbutils.pooled_db import PooledDB
import redis


class Mysql_server:

    def __init__(self):
        self.host = '127.0.0.1'
        self.user = 'root'
        self.passwd = '123456'
        self.db = 'qztd'
        self.port = 3306
        self.charset = 'utf8mb4'
        self.pool = PooledDB(pymysql, 10, host=self.host, user=self.user, passwd=self.passwd, db=self.db,
                             port=self.port, charset=self.charset)  # 5为连接池里的最少连接数

        self.conn = self.pool.connection()  # 以后每次需要数据库连接就是用connection（）函数获取连接就好了

    def get_cursor(self):
        try:
            self.conn.ping()
        except:
            try:
                self.conn = self.pool.connection()
            except:
                self.pool = PooledDB(pymysql, 10, host=self.host, user=self.user, passwd=self.passwd, db=self.db,
                                     port=self.port, charset=self.charset)  # 5为连接池里的最少连接数
                self.conn = self.pool.connection()  # 以后每次需要数据库连接就是用connection（）函数获取连接就好了
                self.conn = self.pool.connection()
        cursor = self.conn.cursor()
        return cursor

    def close(self):
        self.conn.close()


class MongoDBserver():
    def __init__(self):
        self.client = pymongo.MongoClient('127.0.0.1', 27017, maxPoolSize=100)
        self.db = self.client.amazon
        self.collection = self.db.detail_info

    def get_collection(self):
        return self.collection

    def close(self):
        self.client.close()


class RedisDBserver():
    def __init__(self):
        self.pool = redis.ConnectionPool(host='127.0.0.1', port=6379, decode_responses=True)

    def get_collection(self):
        self.r = redis.Redis(connection_pool=self.pool)
        return self.r

    def close(self):
        pass


if __name__ == '__main__':
    # my = Mysql_server()
    # cursor = my.get_cursor()
    # cursor.execute('select id, anser_id from anser where states=0 limit 2')
    # data = cursor.fetchall()
    # print(data)
    # cursor.close()
    # my.close()
    r = RedisDBserver()
    collection = r.get_collection()
    keys = collection.keys()
    print(keys)
