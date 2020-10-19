import re
import time
import random
from lxml import etree
from selenium import webdriver
from pyquery import PyQuery as pq
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from mysql_server import Mysql_server


class CategorySupplement(object):
    def __init__(self, site='us'):
        self.site = site
        options = webdriver.ChromeOptions()
        options.add_argument('lang=en')
        prefs = {'profile.managed_default_content_settings.images': 2}
        options.add_experimental_option('prefs', prefs)
        self.browser = webdriver.Chrome(chrome_options=options)
        self.wait = WebDriverWait(self.browser, 10)
        self.mysql_server = Mysql_server()
        self.cursor = self.mysql_server.get_cursor()
        self.countryArr = {
            "de": "https://www.amazon.de/", "fr": "https://www.amazon.fr/", "uk": "https://www.amazon.co.uk/",
            "jp": "https://www.amazon.co.jp/", "us": "https://www.amazon.com/", "it": "https://www.amazon.it/",
            "es": "https://www.amazon.es/", "ca": "https://www.amazon.ca/", "au": "https://www.amazon.com.au/",
        }
        self.cookies_list = {
            'us': [
                'session-id=147-8333591-9758622; ubid-main=130-3884127-5100529; skin=noskin; session-token=FcrgJrciPNhG+AEYp1gHtGkDkqmjWQqYPzqYWTI4fLyOCg4EZSkATF0YUeQDqPHFk/x9DWfgNcrFMGYiPcW6Wrhm7eIkYNcnASlbMs8qTfrMu6umzYA5BsQ+Z9OM97OJtqVPKg8nbrXNeJzTHKaRIU20Tz+frsKMNRmKFBK4XHXP+3FBm+55LU1UN/O0ipTriWa5Fn99lPUjzz9Hb78rA4E1avMFp8KbTJ4hIYJTCdlki74RAFTMzf2nk0RN/xQVSvMjDCnGJ2zcNi7VUzaPledyQwBagbx9; x-main="HlcsLZ4Gq7XzxS5rmZQXTaD5EW7xI73nKL8h9qlfNMNfOE8o035z5EP4?f47Y61J"; at-main=Atza|IwEBIOnOU7--iHDyKsOiltFuLx-dtMCFjNcnMpKmsGzA08j8J2uLYIMsHNMZNR4QdeYFWAAPs8hSTiEjqaptkbHgKExvqG8KghI0rpQVu9_w9179BjIS_Em7IlSjvL--0aAWoYoVlWzGCrUqul5oH0ojYSTwNnQdt4AAe5_sWY9hFGes7-p0Yndm09X7ymSQWQ-d1yFkSVveWRbV09a4AZePywbm; sess-at-main="3QorUsauzcHl3UyVZ4KL5xzYMG027qJ+/OKSxqm6UGI="; sst-main=Sst1|PQHarY1O5hurB5muBtN9Yu5ZCe9uE1YOdn2dkPVUnEA1MOxvpjAgcfuh3n2MiykhdYoe39tM3pduszP9vggv3H84TOHj4JT83gsk97ZXMbOkI0RoFdmWPAFOk-KaOfFLaZTaFaRvMpU_i50BDCLmTF7b4J0XSDZCGXiA87L7t0H24-FtdU5CYyc5Ef7t7J7jaUJ1fMBNWpW0uyfR-OGRae6kRbB6afuJiXZ9vOH-pXiES3QSuf9hd4znAATAskcYlYhmPqid_4NmTcXrzITr3LH8N7kxjggktbkEOzXrQc5cjho; lc-main=en_US; session-id-time=2082787201l; i18n-prefs=USD; sp-cdn="L5Z9:GB"; csm-hit=tb:s-EW60VBXATHNYN8EMCSW5|1600761482564&t:1600761486768&adb:adblk_no',
            ],
            'uk': [

            ],
            'de': [

            ],
            'fr': [

            ],
            'it': [

            ],
            'es': [

            ],
            'jp': [

            ],
        }

    def set_cookies(self):
        for line in random.choice(self.cookies_list.get(self.site, 'us')).split('; '):
            cookies_dict = {}
            temp = line.split('=', 1)
            cookies_dict['name'] = temp[0]
            cookies_dict['value'] = temp[-1]
            self.browser.add_cookie(cookies_dict)

    def get_data(self):
        select_sql = f"select url from category_supplement where state=0 and country=%s limit 1"
        self.cursor.execute(select_sql, (self.site,))
        data = self.cursor.fetchall()
        for record in data:
            parmas = (record[0])
            update_sql = f"""update category_supplement set state=1 where url=%s"""
            self.cursor.execute(update_sql, parmas)
        self.mysql_server.conn.commit()
        return data

    def insert_data(self, item):
        # 更新类目补充表
        params = (item['bigCategoryName'], item['bigRank'], item['smallCategoryName'], item['smallRank'],
                  item['url'])
        update_sql = f"""update category_supplement set bigCategoryName=%s, bigRank=%s, smallCategoryName=%s, smallRank=%s, state=2 where url=%s"""
        self.cursor.execute(update_sql, params)
        self.mysql_server.conn.commit()
        print('{}更新成功'.format(item['url']))

    def start(self):
        # 先登录，在爬取数据
        self.browser.get(self.countryArr.get(self.site, 'us'))
        self.set_cookies()
        data = self.get_data()
        for record in data:
            item = self.spider_parse(record[0])
            self.insert_data(item)
            print(item)
        self.close_link()

    def spider_parse(self, url):
        item = {}
        flag = 1
        item['url'] = url
        item['asin'] = url.split('/')[-1]
        try:
            self.browser.get(url)
            self.wait.until(EC.presence_of_element_located((By.ID, 'navFooter')))
            html = self.browser.page_source
            doc = pq(html)
            sec = etree.HTML(html)
            # 获取类目，排名
            tr_list = doc('#productDetails_detailBullets_sections1>tbody>tr').items()
            if tr_list:
                for tr in tr_list:
                    th = tr('th').text()
                    td = tr('td').text()
                    if self.site in ['us']:
                        if th == 'Best Sellers Rank':
                            flag = 0
                            bigCategory = list(map(str.strip, td.split('#')[1].split(' in ')))
                            smallCategory = list(map(str.strip, td.split('#')[-1].split(' in ')))
                            bigCategoryName = bigCategory[1].split(' (')[0]
                            bigRank = int(''.join(bigCategory[0].split(',')))
                            smallCategoryName = smallCategory[-1]
                            smallRank = int(''.join(smallCategory[0].split(',')))
                            item['bigCategoryName'] = bigCategoryName
                            item['bigRank'] = bigRank
                            item['smallCategoryName'] = smallCategoryName
                            item['smallRank'] = smallRank
                    if self.site in ['de']:
                        if th == 'Amazon Bestseller-Rang':
                            flag = 0
                            bigCategory = list(map(str.strip, td.split('Nr. ')[1].split(' in ')))
                            smallCategory = list(map(str.strip, td.split('Nr. ')[-1].split(' in ')))
                            bigCategoryName = bigCategory[1].split(' (')[0]
                            bigRank = int(''.join(bigCategory[0].split(',')))
                            smallCategoryName = smallCategory[-1]
                            smallRank = int(''.join(smallCategory[0].split(',')))
                            item['bigCategoryName'] = bigCategoryName
                            item['bigRank'] = bigRank
                            item['smallCategoryName'] = smallCategoryName
                            item['smallRank'] = smallRank
            ul_list = doc('#detailBulletsWrapper_feature_div>ul').items()
            if ul_list:
                for ul in ul_list:
                    title = ul('li>span>span').text()
                    if self.site in ['de']:
                        if title == 'Amazon Bestseller-Rang:':
                            flag = 0
                            content = ul('li').text()
                            bigCategory = list(map(str.strip, content.split('Nr. ')[1].split(' in ')))
                            smallCategory = list(map(str.strip, content.split('Nr. ')[-1].split(' in ')))
                            bigCategoryName = bigCategory[1].split(' (')[0]
                            bigRank = int(''.join(bigCategory[0].split(',')))
                            smallCategoryName = smallCategory[-1]
                            smallRank = int(''.join(smallCategory[0].split(',')))
                            item['bigCategoryName'] = bigCategoryName
                            item['bigRank'] = bigRank
                            item['smallCategoryName'] = smallCategoryName
                            item['smallRank'] = smallRank
            if flag:
                item['bigCategoryName'] = ''
                item['bigRank'] = 0
                item['smallCategoryName'] = ''
                item['smallRank'] = 0
            # 获取价格
            price = doc('#priceblock_ourprice').text()
            # 获取跟卖最低价
            min_price = doc('.olp-text-box>span:nth-child(3)').text()
            # 获取Rating
            rating_star = doc('span[data-hook="rating-out-of-text"]').text()
            rating_num = doc('#acrCustomerReviewText').text()
            star_section = doc('#histogramTable>tbody>tr').items()
            stars = ['five', 'four', 'three', 'two', 'one']
            for line, star in zip(star_section, stars):
                item[star] = line('td:nth-child(3)').text()
            # 获取label
            label_section = doc('div[cssclass="aok-float-left"]>span').items()
            label = ''
            best_seller = ''
            new_release = ''
            amazon_choice = ''
            for i, line in enumerate(label_section):
                if i == 0:
                    label = line.text()
                else:
                    if label == "Best's Seller":
                        best_seller = line.text().split('"')[1]
                    if label == "New's Release":
                        new_release = line.text().split('"')[1]
                    if label == "Amazon's Choice":
                        amazon_choice = line.text().split('"')[1]
            # 获取卖家类型
            seller1 = ''.join(sec.xpath('//*[@id="buybox-tabular"]//text()'))
            seller2 = ''.join(sec.xpath('//*[@id="merchant-info"]//text()'))
            seller1_url = ''.join(sec.xpath('//*[@id="buybox-tabular"]//a[@id="sellerProfileTriggerId"]/@href'))
            seller2_url = ''.join(sec.xpath('//*[@id="merchant-info"]//a[@id="sellerProfileTriggerId"]/@href'))
            if 'Amazon' in seller1 or 'Amazon' in seller2:
                seller_type = 'AMZ'
            elif 'isAmazonFulfilled' in seller1_url or 'isAmazonFulfilled' in seller2_url:
                seller_type = 'FBA'
            else:
                seller_type = 'MAH'
            item['price'] = float(re.findall(r"\d+\.?\d*|$", price)[0] or 0)
            item['min_price'] = float(re.findall(r"\d+\.?\d*|$", min_price)[0] or 0)
            item['rating_star'] = float(re.findall(r"\d+\.?\d*|$", rating_star)[0] or 0)
            item['rating_num'] = int(re.findall(r"\d+\.?\d*|$", rating_num.replace(',', ''))[0] or 0)
            item['best_seller'] = best_seller
            item['new_release'] = new_release
            item['amazon_choice'] = amazon_choice
            item['seller_type'] = seller_type
        except Exception as e:
            print('识别验证码')
        return item

    def close_link(self):
        self.browser.close()
        self.mysql_server.close()


if __name__ == '__main__':
    c = CategorySupplement(site='us')
    c.start()
