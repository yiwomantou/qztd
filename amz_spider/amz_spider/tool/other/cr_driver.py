# -*- coding: utf-8 -*-
import time
import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import traceback
from lxml import etree
from mysql_server import Mysql_server


class Webdriver:
    def __init__(self):  # 进入目标页面完成条件选择
        self.timetamp = 0
        # self.re_db = db
        # self.logger = logs
        # self.hostname = info.get_vm_id()
        # self.task_name = 'fb:task:L_keyword2'

        # proxy = self.re_db.redis_server.srandmember('fb:tmp:T_bigspy_proxy')
        # print '本次取到的代理是%s' % proxy
        # ------------------以下为浏览器设置------------------
        options = webdriver.ChromeOptions()  # 保存浏览器设置
        # options.add_argument('--headless')  # 设置为无头浏览器
        options.add_argument('--no-sandbox')
        options.add_argument('window-size=1800x1200')  # 设置分辨率，改变分辨率可能会报错
        options.add_argument('--disable-dev-shm-usage')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('blink-settings=imagesEnabled=false')  # 不加载图片
        # options.add_argument('--disable-gpu')  # 谷歌文档指示用此规避bug
        # options.add_argument('--proxy-server=socks5://{}'.format(proxy))
        self.driver = webdriver.Chrome(executable_path=r'C:\Users\Administrator\Desktop\chromedriver',
                                       options=options)  # chromedriver加载路径
        self.mysql_server = Mysql_server()
        self.cursor = self.mysql_server.get_cursor()

    def search_keyword(self,result):  # 搜索关键词并翻页抓取数据
        self.driver.get(
            "https://www.amazon.com/useasdfas")  # 访问域名错误网址提高访问速度
        # print '访问目标网站'
        self.driver.delete_all_cookies()  # 清空cookie
        print('清除cookies成功')
        # self.logger.send_log(2, 'info', 0, self.task_name, 'cookies清空成功')
        cookies_list =[{'name':'at-main','value':'Atza|IwEBIDq-tcGtZ5Lf2qGlo-Jx-I8Nmj-zdL8fDE0HHBioM6G93GGei0Mm4SMkcaXLamums_RWRUhLyrHwDtSnMMhXpLEhvM-tIeWmk-A0SS9niEPWcYsHWv0dTK4k1XEjJqdqJ6iAXs88Ew7uQLQnsNTN 4nCMTc-ORuzBQkVGtYWr4_rA3dAhfsoAxpvpD-ffJ-CBtDIPGy66bISjJKhrbnqV0M5p'},{'name':'i18n-prefs','value':'USD'},{'name':'lc-main','value':'en_US'},{'name':'sess-at-main','value':'"WlLZSEIEDkCpcJt0H1Ce6T/eviKikSuhVuWT3rjmoWA="'},{'name':'session-id','value':'136-4121725-0711760'},{'name':'session-id-time','value':'2082787201l'},{'name':'session-token','value':'"kx8hP/YwoFHtrdRsaFlg5WOOxFEHV9hE673M6UXLa0FolbSICki5Yf1LldSTNzwliM/2BUUKGBQGEJSzG2v/EowMHjfVponbFbBzYJdQJiD3gy+H97My+88SZbpezacQks09IsvL221gihflK7xDZfopw38w Avti11mA3VBgezXK0WBxVQsQf2YrbE9cojVtTuiAnwQpHijNSqrDjkHpc4XjFklT//s0r3zAtJfvUBQ="'},{'name':'skin','value':'noskin'},{'name':'sst-main','value':'Sst1|PQHnI_uqobgK49iODGOze2zQCSEM5raUp9WBX5c47QGvR21f9fqVrrOTRzq1pCWmPXfiiGRqS9MDWboit6cfF0druQDYMi9QenzgBkCs098EOqh49OGy6aLRSybM_OwszNrt_q6yR32wjX8QKti6k7gu 4ArA-3ROmiVQvsKQ2QqxQgVcMeg2ZalQtI1i14lYaVlcASDwvvnEwk2WWDwyH0c_0Kygd2o0NM_EvMLvynxquN1JW-9X9Yn-6Bzbbnn_lgvLUhvqKLDOpsoPcu2SF_Nbwl1GoUw7Zl1pgUyApslxPc0'},{'name':'ubid-main','value':'133-4259985-7368459'},{'name':'x-main','value':'"n8?qv4?9dm2glV7Og4OhEZZdP87UuvfW1VRrNiAA5SAy8BczTboe69ITC3xh9wt1"'},{'name':'csm-hit','value':'tb:s-FPWHYBK8VP48D94STPED|1600740750863&t:1600740752601&adb:adblk_no'}]
        for cookie in cookies_list:
            self.driver.add_cookie(cookie)
        # self.logger.send_log(2, 'info', 0, self.task_name, 'cookies注入成功')
        print('cookies注入成功')
        self.driver.get("https://www.amazon.com")  # 访问网站首页
        self.driver.find_element_by_id('twotabsearchtextbox').clear()
        self.driver.find_element_by_id('twotabsearchtextbox').send_keys('%s' % result['keyword'])
        print('清空并输入关键词')
        time.sleep(1)
        print('搜索关键词')
        self.driver.find_element_by_id('twotabsearchtextbox').send_keys(Keys.ENTER)
        time.sleep(10)
        try:
            self.driver.find_elements_by_xpath('//div[@class="s-main-slot s-result-list s-search-results sg-row"]')
            return True
        except:
            return False

    def next_page(self):
        try:
            # print '开始翻下一页'
            self.driver.find_element_by_xpath('//li[@class="a-last"]').click()
            time.sleep(8)
            return True
        except:
            print('翻页失败')
            return False

    def close_driver(self):  # 关闭页面及浏览器
        self.mysql_server.close()
        self.driver.quit()

    def parse(self, page, position_num, ad_position):
        source = self.driver.page_source #获取网页源代码
        # print(source)
        response = etree.HTML(source)
        results = response.xpath('//div[@class="s-main-slot s-result-list s-search-results sg-row"]/div[@data-asin]')
        # print(len(results))
        for result in results:
            result_dict = {}
            result_dict['pageNum'] = page  # asin所在页数
            asin = result.xpath('@data-asin')[0]  # 提取asin
            if asin != '':
                result_dict['asin'] = asin
                position_num += 1
                result_dict['positionNum'] = position_num  # 所在页面位置
                # 判断是否为广告位   # Todo: 英国站有时候会出现无任何广告位现象
                ad_str = result.xpath('./div//span/span/span/span/text()')
                ad_str = '' if len(ad_str) ==0 else ad_str[0]

                if ad_str in ["Sponsored", "Sponsorisé", "Sponsorizzato", "Patrocinado", "スポンサー プロダクト", "Gesponsert"]:
                    ad_position += 1
                    position_num -= 1
                    result_dict['positionNum'] = ad_position  # 所在页面位置
                    result_dict['ad'] = 1
                else:
                    result_dict['ad'] = 0
                # 判断是否为amz choice标签
                amz_choice = result.xpath(f'.//span[@id="{asin}-amazons-choice-supplementary"]/text()')
                if len(amz_choice) > 0:
                    result_dict['amz_choice'] = amz_choice[0].replace('for ', '')
                else:
                    result_dict['amz_choice'] = ''

                # 判断是否有bsr 标签
                bsr_label = result.xpath(f'.//span[@id="{asin}-best-seller-supplementary"]/text()')
                if len(bsr_label) > 0:
                    result_dict['bsr_category'] = bsr_label[0].replace('in ', '')
                else:
                    result_dict['bsr_category'] = ''

                result_dict['keyword'] = 'hub'
                result_dict['country'] = 'us'
                result_dict['state'] = 1
                self.save_data(result_dict)
                # print(result_dict)

        # 获取下一页url
        temp_url = response.xpath('//ul[@class="a-pagination"]/li[@class="a-last"]/a/@href')
        if len(temp_url) > 0:
            return True, position_num, ad_position
        else:
            return False, 0, 0

    def get_task(self):
        sql = """select keyword, country from keywords where state=0"""
        self.cursor.execute(sql)
        data_list = self.cursor.fetchall()
        task_list = []
        for i in data_list:
            keyword = i[0]
            country = i[-1]
            task = {'keyword': keyword, 'country': country}
            parmas = (task['keyword'],)
            update_sql = """update keywords set state=1 where keyword=%s"""
            self.cursor.execute(update_sql, parmas)
            task_list.append(task)
        self.mysql_server.conn.commit()
        return task_list

    def save_data(self, data):
        timestamp = int(time.time())
        params = (data['asin'], data['pageNum'], data['positionNum'],
                  data['keyword'], timestamp, data['ad'], data['amz_choice'], data['bsr_category'])
        sql = f"""insert into us_asins (id, asin, pageNum, positionNum, keyword, timestamp,state, ad, amz_choice, bsr_category)
                 values (0, %s, %s, %s, %s, %s, 0, %s, %s, %s)"""
        self.cursor.execute(sql, params)



def run():
    web = Webdriver()
    task_list = web.get_task()
    print(task_list)
    for task in task_list:
        result = web.search_keyword(task)
        page = 1
        result, position_num, ad_position = web.parse(page, 0, 0)
        web.mysql_server.conn.commit()
        while result:
            page +=1
            if page <= 5:
                result = web.next_page()
                if result:
                    result, position_num, ad_position = web.parse(page, position_num, ad_position)
                    web.mysql_server.conn.commit()
                else:
                    break
            else:
                break
    web.close_driver()
    pass


if __name__ == '__main__':
    run()
