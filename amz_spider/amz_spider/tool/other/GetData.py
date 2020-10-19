# coding: utf-8
# 用于提取asin的各个评分等级的评论

from mysql_server import Mysql_server


class ReviewData():

    def __init__(self):
        self.sql_server = Mysql_server()

    def get_data(self, asin, raiting):
        # 根据asin提取指定评分的评论
        self.cursor = self.sql_server.get_cursor()
        sql = """select review_title, review_body
                 from product_reviews 
                 where asin=%s and review_raiting=%s"""
        params = (asin, raiting)
        self.cursor.execute(sql, params)
        data_list = self.cursor.fetchall()
        # 将评论写入文件,便于下一步进行词频统计
        for data in data_list:
            with open(f'{asin}_{raiting}.txt', 'a', encoding='utf-8') as f:
                f.write(data[0])
                f.write("        ")
                f.write(data[-1])
                f.write("\n")
        self.sql_server.close()

    def get_otherdata(self):
        self.cursor = self.sql_server.get_cursor()
        sql = ""


if __name__ == '_main__':
    r = ReviewData()
    # asin列表，手动填写
    asin_list = [
        # "B01N0993NM",
        "B07145GM4B",
        "B01DXNHMHE",
        "B07MCSTVMV",
        "B00GUGIFF0",
        "B07FCCMWZN",
        "B07N86NW4X",
        "B07WHYLM3M",
        "B07M5LWC36",
        "B07QTZCQ8Y",
    ]
    for asin in asin_list:
        for rating in range(1,6):
            r.get_data(asin, rating)
    print('===')
