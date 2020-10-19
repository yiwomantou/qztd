import pymysql
from DBUtils.PooledDB import PooledDB


class Mysql_server:
    def __init__(self):
        self.host = '127.0.0.1'
        self.user = 'root'
        self.passwd = '123456'
        self.db = 'zol'
        self.port = 3306
        self.charset = 'utf8mb4'
        self.pool = PooledDB(pymysql, 10, host=self.host, user=self.user, passwd=self.passwd, db=self.db,
                             port=self.port, charset=self.charset)  # 5为连接池里的最少连接数
        self.conn = self.pool.connection()  # 以后每次需要数据库连接就是用connection函数获取连接就好了

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

        cursor = self.conn.cursor()
        return cursor

    def close(self):
        self.conn.close()


if __name__ == '__main__':
    pass
