import pymysql
import pymongo


# 导包出现问题，将mysql_server.py文件搬运此处   Todo: 解决导包路径问题


class Mysql_server:

    def __init__(self):
        self.host = '127.0.0.1'
        self.user = 'root'
        self.passwd = '123456'
        self.db = 'qztd'
        self.port = 3306
        self.charset = 'utf8mb4'
        self.conn = pymysql.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.db, port=self.port,
                                    charset=self.charset)

    def get_cursor(self):
        try:
            self.conn.ping()
        except:
            self.conn = pymysql.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.db, port=self.port,
                                        charset=self.charset)
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


if __name__ == '__main__':
    # my = Mysql_server()
    # cursor = my.get_cursor()
    # cursor.execute('select id, anser_id from anser where states=0 limit 2')
    # data = cursor.fetchall()
    # print(data)
    # cursor.close()
    # my.close()
    s = MongoDBserver()
