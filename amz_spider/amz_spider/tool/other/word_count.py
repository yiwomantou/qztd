# coding=utf-8
# 词频统计分析

import jieba
from mysql_server import Mysql_server
import re
import os


class WordCount():
    def __init__(self):
        pass

    def save_txt(self, sql):
        # 将MySQL查询得到的数据存入本地的txt文件
        my = Mysql_server()
        cursor = my.get_cursor()
        cursor.execute(sql)
        data_list = cursor.fetchall()
        cursor.close()
        my.close()
        for data in data_list:
            with open('reviews/WordCount.txt', 'a', encoding='utf-8')as f:
                f.write(' ')
                f.write(data[0].lower())
                f.write('\n')
                f.write(data[-1].lower())
                f.write('\n')
        print('写入完毕')

    def process_file(self, keyword, filename, password_filename):
        # 对文件的词频进行统计
        # 如果keyword为None则进行整体数据的词频统计
        if keyword == None:
            with open(f"reviews/{filename}", encoding="utf-8") as f:
                txt = f.read().lower()
        # 如果不为None则表示对某个词的附近词的文件进行词频统计
        else:
            with open(f"result_{keyword}.txt", encoding="utf-8") as f:
                txt = f.read().lower()
        # 加载停用词表，将在停用词表中的词从结果中过滤出去
        stopwords = [line.strip() for line in
                     open(f"reviews/pass_words/{password_filename}", encoding="utf-8").readlines()]
        words = jieba.lcut(txt, cut_all=True)
        counts = {}
        for word in words:
            # 不在停用词表中
            if word not in stopwords:
                # 不统计字数为一的词
                if len(word) == 1:
                    continue
                else:
                    counts[word] = counts.get(word, 0) + 1
        items = list(counts.items())
        # 对结果进行排序
        items.sort(key=lambda x: x[1], reverse=True)
        # 如果是对整体数据进行词频统计则保存结果前100条，否则为30条
        if keyword is None:
            num = 101
            keyword = ""
        else:
            num = 21
        for i in range(1, num):
            try:
                word, count = items[i]
                print("{:<10}{:>7}{:>10}".format(word, count, keyword))
                # 将打印的结果写入文件保存
                with open(f'{filename.replace(r".txt", "")}.txt', 'a') as h:
                    h.write("{:<20}{:<20}{:<20}".format(word, count, keyword))
                    h.write('\n')
            except:
                print("-----------------------")

    def get_word_list(self, filename):
        with open(f'{filename.replace(r".txt", "")}.txt', 'r')as f:
            content = f.readlines()
        word_list = []
        for data in content:
            word_list.append(data.split(' ')[0])
        return word_list


def re_test(word_list, filename):
    # 从源文件中匹配出关键词附近的5个词，并写入文件
    for word in word_list:
        with open(f'reviews/{filename}', 'r', encoding='utf-8') as f:
            content = f.readlines()
        for words in content:
            # result_list = re.findall('(([^\s]+ ){0,5}%s( [^\s]+){0,5})'%word, words)
            try:
                result_list = re.findall('(([^\s]+ ){0,5}%s( [^\s]+){0,5})' % word, words.lower())[0][0]
                # for result in result_list:
                with open(f'result_{word}.txt', 'a', encoding='utf-8')as s:
                    s.write(result_list)
                    s.write('\n')
            except:
                pass
        print(f'---已处理完:{word}---')


def remove_file():
    # 删除词频分析的其他结果，只保留最后的目标文件
    path = r"E:\spider\spider_project\amazon\amz_spider\amz_spider\tool\other"
    file_name_list = os.listdir(path)
    for filename in file_name_list:
        if filename.startswith('result_'):
            os.remove(filename)


def handle_review():
    # 产品分析时提取指定3个asin的评论进行词频分析
    word_count = WordCount()
    # filename = "B07M5LWC36_5.txt"
    asin_list = [
        'B01N21O2EV',
        'B0797GBRP8',
        'B00E0O2GF4',
    ]
    for asin in asin_list:
        filename = f"{asin}.txt"
        word_count.process_file(keyword=None, filename=filename, password_filename='hair_removel_en_pass_word.txt')
        word_list = word_count.get_word_list(filename)
        re_test(word_list, filename=filename)
        for word in word_list:
            try:
                word_count.process_file(keyword=word, filename=filename,
                                        password_filename='hair_removel_en_pass_word.txt')
            except:
                print('===')
        remove_file()


def handle_file():
    # 市场分析时，先手动从数据库导出关键词的所有asin的评论标题和内容存为文本，再进行词频统计
    word_count = WordCount()
    filename = "product_reviews.txt"
    word_count.process_file(keyword=None, filename=filename, password_filename='hair_removel_en_pass_word.txt')
    word_list = word_count.get_word_list('product_reviews.txt')
    re_test(word_list, filename=filename)
    for word in word_list:
        try:
            word_count.process_file(keyword=word, filename=filename, password_filename='hair_removel_en_pass_word.txt')
        except:
            print('===')
    remove_file()


if __name__ == '__main__':
    handle_review()
    # handle_file()
