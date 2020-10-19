# coding: utf-8
# 用于临时插入爬取评论任务

from mysql_server import Mysql_server

class InsertData():

    def __init__(self, file_path):
        self.sql_server = Mysql_server()
        with open(file_path, 'r', encoding='utf-8') as f:
            self.data_list = f.readlines()

    def insert_data(self):
        self.cursor = self.sql_server.get_cursor()
        i = 0
        print(self.data_list)
        for data in self.data_list[1:]:
            info_list = data.replace('\n', '').split(',')[0]
            # try:
            print(info_list,'===')
            sql = f"""insert into us_asins (id, asin, keyword, pageNum, positionNum, ad,state, timestamp) values(0, '{info_list}', 'tuoyuanji', 1,1, 0, 5, 1)"""
            print('====', sql)
            self.cursor.execute(sql)
            self.sql_server.conn.commit()
            # except:
            #     i +=1
            #     print(i)
        self.sql_server.close()


if __name__ == '_main__':
    print('=============')
    # 从文件读取asin插入任务表
    insert = InsertData(r'1.txt')
    insert.insert_data()

