# -*- coding: utf-8 -*-
import scrapy
import re
import json
# import requests
import socket
# import time
# from pprint import pprint
import time
# from urllib import parse
from copy import deepcopy
# from mysql_server import Mysql_server
from amz_spider.tool.db.mysql_server import Mysql_server, RedisDBserver


# import logging
# from smspider.tool.log.log_ctr import log
# import smspider.tool.log.log_data

# logger = logging.getLogger('best_sellers')


class AmzRankSpider(scrapy.Spider):
    name = 'rank100'
    allowed_domains = ['amazon.com']

    # 在0-2点同时返回热点数据和日常数据
    # hot_flag = 1
    # time_flag = 1
    # day_time = time.localtime()
    # day_time = time.strftime('%Y_%m_%d', day_time)
    # # low_time = day_time + ' 09:00:00'
    # low_time = day_time + ' 16:00:00'
    # up_time = day_time + ' 17:59:59'
    # # up_time = day_time + ' 10:59:59'
    # low_timestamp = int(time.mktime(time.strptime(low_time, '%Y_%m_%d %H:%M:%S')))
    # up_timestamp = int(time.mktime(time.strptime(up_time, '%Y_%m_%d %H:%M:%S')))
    # if int(time.time()) <= up_timestamp and int(time.time()) >= low_timestamp:
    #     hot_flag = 0
    #
    # # if int(time.time()) < up_timestamp:
    # if int(time.time()) < low_timestamp:
    #     time_flag = 0
    #
    # num = 1
    # # sr = StrictRedis(host='52.82.24.19',port=6379,password='smedu')
    # # proxy = 'http://127.0.0.1:8888'

    headers = {
        'authority': 'www.amazon.com',
        'cache-control': 'max-age=0',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
    }
    cookies = 'csm-hit=tb:s-020TYSQEV85MVK4CBRQN|1579514359902&t:1579514360000&adb:adblk_no; at-main=Atza|IwEBIMzR1ouHist7JnPK1R9PGtnQfLaWjrehd4eFckJKZKnX1EldFksVU1LSeqRnDLg1a4Z_HaICKFTfSocmdBwFVlXyftxGHsC6o4_98mdeCzgwt-GHhrOfteBQlm1C9s591_GA-Fld2CPLZISE5FAPJ4Mvyr2MCed79l1TeTMiozfROx3Ubfyv56BXrs0v6-pht9nTFwwEv-eH5Mm9Atib0jei4Xk5oCHJSpP5BOJIlsovCsFmttSJEzM9MhjOMcHnkmtAWUT-LbG8tCJigHELAGUl63eNypq3ZxRjwQjO5y4Uk9BhawL4chg0gzZMeHhBDugm_xedmPFIcnnr_c9oUEr8C4boAEw5ov9mUjZxCQkCsnrCYgStS8i2BAq4Aq7gdfwfBUpw9sPSCJZu6gb1nbyy; sst-main=Sst1|PQFpWD-VgdEmGAscWARZR82_Czl_g5lrKoxvR99pwXvldJUtbsfSGcj5SKAm2mqYpwRIWuw_GZuyfD0h_WXdPrRXdkE480b71NOcmV5QP_TVmz2YFj7gcpXQDjg7OVrGWyq9zDA8O8Hd6lcLauPo981DlSfgXsddrXOjKS8Kw2PrnTsAKUp67lb5PwbyztsLvSyrSzSWNnhyttRUafVLW-GDNI5tjyaxSwNxFg5_pxLZeO7bSFamwnxQxmR7rBPNOOOqObkuQi2pzhA_hXuERrhZq47m31yK3iRrcQWZrlM0lcvKLsJ0IHm1-_hgzeXcr8yvqYqq2kqvr40ubGsZlwFV4Q; sess-at-main="SzTFaYLeX3JHPqVGkFIhtcAoemG+X6OuoGXbddTUz+E="; lc-main=en_US; x-main="qeJYfX7Fc1TbdeXBWHDtokyWnm3@xIb0bI9geaz?4nD@0OaNZO4UWcP6JjyeyxR2"; a-ogbcbff=1; x-wl-uid=13UGgXJyehq61rfsaUAq+eI2M/gqJzLEeKliCrEG3br6NlS8UPjZrWH8HmT23iYdrmlJvOuNfUFo=; ubid-main=132-1348326-1496835; session-id=139-7888532-6481302; i18n-prefs=USD; sp-cdn="L5Z9:CN"; session-id-time=2082787201l; s_fid=452FDC96AB71A086-38333C2514B0BDE2; regStatus=pre-register; s_cc=true; aws-priv=eyJ2IjoxLCJzdCI6MX0=; s_vn=1615541632501%26vn%3D4; s_dslv=1584351163862; s_nr=1584351163870-Repeat; s_sq=%5B%5BB%5D%5D; session-token=hROV4uS23F0L6N0/9pBTjgjiidpbw3CiCGeOdEoLPT6pa4Fd4cM/RqNrNbzlZRwxLL1oXq3K7J3bMUauFcC5O4110uEsQj8yfBL1G/8tsOwuRZJho86Lke7IXzBlAjocJzywutzG9HL/FfgDsXvs1HD+mfkMzXz+GeSxgsY+diQ02fCKk0Vni8P2nI740HrlNnw5dwUrRaO19LF3D4uA6Ze87/wuenM/NNzpWYOUtgXkoc5yKdVWoGFIabrB3uQ/HNqUQsM84G4=; csm-hit=tb:3YHPD552H8XF3889RB1H+s-5YB10XCABFPQ830Q9SSQ|1584409923911&t:1584409923911&adb:adblk_no'

    cookies = {i.split("=", 1)[0]: i.split("=", 1)[1] for i in cookies.split("; ")}

    custom_settings = {
        'HTTPERROR_ALLOWED_CODES': [500, 502, 503, 400, 404, 443, 415],
        'ITEM_PIPELINES': {'amz_spider.pipelines.AmzbsrPipeline': 300},
        'DOWNLOADER_MIDDLEWARES': {
            'amz_spider.middlewares.ProxyMiddleware': 400,
        },
        'CONCURRENT_REQUESTS': 1,
        # 'COOKIES_ENABLED':False,
        'DOWNLOAD_DELAY': 3,
    }

    def __init__(self):
        pass

    def start_requests(self):
        # lev1_list = [
        #     # {'cat_url': 'https://www.amazon.com/Best-Sellers/zgbs/amazon-devices/',
        #     #  'category_name': 'Amazon Devices & Accessories', 'level': 1},
        #     # {'cat_url': 'https://www.amazon.com/Best-Sellers-Amazon-Launchpad/zgbs/boost/',
        #     #  'category_name': 'Amazon Launchpad', 'level': 1},
        #     # {'cat_url': 'https://www.amazon.com/Best-Sellers-Prime-Pantry/zgbs/pantry/', 'category_name': 'Amazon Pantry',
        #     #  'level': 1},
        #     # {'cat_url': 'https://www.amazon.com/Best-Sellers-Appliances/zgbs/appliances/', 'category_name': 'Appliances',
        #     #  'level': 1}, {'cat_url': 'https://www.amazon.com/Best-Sellers-Appstore-Android/zgbs/mobile-apps/',
        #     #                'category_name': 'Apps & Games', 'level': 1},
        #     # {'cat_url': 'https://www.amazon.com/Best-Sellers-Arts-Crafts-Sewing/zgbs/arts-crafts/',
        #     #  'category_name': 'Arts, Crafts & Sewing', 'level': 1},
        #     # {'cat_url': 'https://www.amazon.com/Best-Sellers-Audible-Audiobooks/zgbs/audible/',
        #     #  'category_name': 'Audible Books & Originals', 'level': 1},
        #     # {'cat_url': 'https://www.amazon.com/Best-Sellers-Automotive/zgbs/automotive/', 'category_name': 'Automotive',
        #     #  'level': 1},
        #     # {'cat_url': 'https://www.amazon.com/Best-Sellers-Baby/zgbs/baby-products/', 'category_name': 'Baby', 'level': 1},
        #     {'cat_url': 'https://www.amazon.com/Best-Sellers-Beauty/zgbs/beauty/', 'category_name': 'Beauty & Personal Care',
        #      'level': 1, "category_id": 2001911},
        #     # {'cat_url': 'https://www.amazon.com/best-sellers-books-Amazon/zgbs/books/', 'category_name': 'Books',
        #     #  'level': 1},
        #     # {'cat_url': 'https://www.amazon.com/best-sellers-music-albums/zgbs/music/', 'category_name': 'CDs & Vinyl',
        #     #  'level': 1},
        #     {'cat_url': 'https://www.amazon.com/best-sellers-camera-photo/zgbs/photo/', 'category_name': 'Camera & Photo',
        #      'level': 1,"category_id": 2001912},
        #     {'cat_url': 'https://www.amazon.com/Best-Sellers/zgbs/wireless/', 'category_name': 'Cell Phones & Accessories',
        #      'level': 1,"category_id": 2001913},
        #     # {'cat_url': 'https://www.amazon.com/Best-Sellers/zgbs/fashion/', 'category_name': 'Clothing, Shoes & Jewelry',
        #     #  'level': 1}, {'cat_url': 'https://www.amazon.com/Best-Sellers-Collectible-Coins/zgbs/coins/',
        #     #                'category_name': 'Collectible Currencies', 'level': 1},
        #     {'cat_url': 'https://www.amazon.com/Best-Sellers-Computers-Accessories/zgbs/pc/',
        #      'category_name': 'Computers & Accessories', 'level': 1, "category_id": 2001914},
        #     # {'cat_url': 'https://www.amazon.com/Best-Sellers-MP3-Downloads/zgbs/dmusic/', 'category_name': 'Digital Music',
        #     #  'level': 1},
        #     {'cat_url': 'https://www.amazon.com/Best-Sellers-Electronics/zgbs/electronics/', 'category_name': 'Electronics',
        #      'level': 1, "category_id": 2001915},
        #     # {
        #     #     'cat_url': 'https://www.amazon.com/Best-Sellers-Entertainment-Collectibles/zgbs/entertainment-collectibles/',
        #     #     'category_name': 'Entertainment Collectibles', 'level': 1},
        #     # {'cat_url': 'https://www.amazon.com/Best-Sellers-Gift-Cards/zgbs/gift-cards/', 'category_name': 'Gift Cards',
        #     #  'level': 1}, {'cat_url': 'https://www.amazon.com/Best-Sellers-Grocery-Gourmet-Food/zgbs/grocery/',
        #     #                'category_name': 'Grocery & Gourmet Food', 'level': 1},
        #     # {'cat_url': 'https://www.amazon.com/Best-Sellers-Handmade/zgbs/handmade/', 'category_name': 'Handmade Products',
        #     #  'level': 1},
        # {'cat_url': 'https://www.amazon.com/Best-Sellers-Health-Personal-Care/zgbs/hpc/',
        #                    'category_name': 'Health & Household', 'level': 1, "category_id": 2001916},
        #     {'cat_url': 'https://www.amazon.com/Best-Sellers-Home-Kitchen/zgbs/home-garden/',
        #      'category_name': 'Home & Kitchen', 'level': 1,"category_id": 2001917},
        #     # {'cat_url': 'https://www.amazon.com/Best-Sellers-Industrial-Scientific/zgbs/industrial/',
        #     #  'category_name': 'Industrial & Scientific', 'level': 1},
        #     # {'cat_url': 'https://www.amazon.com/Best-Sellers-Kindle-Store/zgbs/digital-text/',
        #     #  'category_name': 'Kindle Store', 'level': 1},
        #     {'cat_url': 'https://www.amazon.com/Best-Sellers-Kitchen-Dining/zgbs/kitchen/',
        #      'category_name': 'Kitchen & Dining', 'level': 1,"category_id": 2001918},
        #     # {'cat_url': 'https://www.amazon.com/Best-Sellers-Magazines/zgbs/magazines/',
        #     #  'category_name': 'Magazine Subscriptions', 'level': 1},
        #     # {'cat_url': 'https://www.amazon.com/best-sellers-movies-TV-DVD-Blu-ray/zgbs/movies-tv/',
        #     #  'category_name': 'Movies & TV', 'level': 1},
        #     # {'cat_url': 'https://www.amazon.com/Best-Sellers-Musical-Instruments/zgbs/musical-instruments/',
        #     #  'category_name': 'Musical Instruments', 'level': 1},
        #     {'cat_url': 'https://www.amazon.com/Best-Sellers-Office-Products/zgbs/office-products/',
        #      'category_name': 'Office Products', 'level': 1,"category_id": 2001919},
        #     {'cat_url': 'https://www.amazon.com/Best-Sellers-Garden-Outdoor/zgbs/lawn-garden/',
        #      'category_name': 'Patio, Lawn & Garden', 'level': 1, "category_id": 2001920},
        #     {'cat_url': 'https://www.amazon.com/Best-Sellers-Pet-Supplies/zgbs/pet-supplies/',
        #      'category_name': 'Pet Supplies', 'level': 1,"category_id": 2001921},
        #     # {'cat_url': 'https://www.amazon.com/best-sellers-software/zgbs/software/', 'category_name': 'Software',
        #     #  'level': 1},
        # {'cat_url': 'https://www.amazon.com/Best-Sellers-Sports-Outdoors/zgbs/sporting-goods/',
        #                    'category_name': 'Sports & Outdoors', 'level': 1,"category_id": 2001922},
        #     # {'cat_url': 'https://www.amazon.com/Best-Sellers-Sports-Collectibles/zgbs/sports-collectibles/',
        #     #  'category_name': 'Sports Collectibles', 'level': 1},
        #     {'cat_url': 'https://www.amazon.com/Best-Sellers-Home-Improvement/zgbs/hi/',
        #      'category_name': 'Tools & Home Improvement', 'level': 1, "category_id": 2001923},
        #     # {'cat_url': 'https://www.amazon.com/Best-Sellers-Toys-Games/zgbs/toys-and-games/',
        #     #  'category_name': 'Toys & Games', 'level': 1},
        #     # {'cat_url': 'https://www.amazon.com/best-sellers-video-games/zgbs/videogames/', 'category_name': 'Video Games',
        #     #  'level': 1}
        # ]

        # code = data['code']
        # if code == 0:
        #     task_list = data['data']
        # for data in task_list:
        # try:
        # categoryId = data['categoryId']
        # categoryId = data['category_id']
        # if categoryId != 0:
        #     if data['level'] == 1:
        #         category_name = data['category_name']
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
            "cookie": "session-id=145-5209209-9478023; i18n-prefs=USD; ubid-main=133-8276981-7688751; x-wl-uid=1PCOyx0JI1kz7vWchZyMhRWJtqj1XoQoE0UNJPLhOT/Q8+kepq170hFhtVj1OBOSit46HW9f+Rz8=; lc-main=en_US; session-id-time=2082787201l; session-token=3TtwIpr/LCK/R5dUusiKqRfu1FQJmG80o4BC0knm7brPg8aelaJ+f/B16GedWlTyDSjn8qQo3s3PmGmw5mHywT8RWHthFHuduD76fCQKbeUHR0G/OJ4sj2eZxXUoxgcWn+a+xbKm+Rpj5ciXMPsk4ObS1HmuF5NFMFttjbT4ZsWQBxh5Ak9x1hxbsqNIrrrW; csm-hit=tb:0YBA58R18R2BQ1H4SWX6+b-0YBA58R18R2BQ1H4SWX6|1592453272955&t:1592453272955&adb:adblk_yes"
        }
        #  从MySQL取状态为0的类目爬取子类目和asin
        mysql_server = Mysql_server()
        cursor = mysql_server.get_cursor()
        cursor.execute(
            f"select category_id, category_name, level, bsr_url,country from amz_category where state=0 and country='de' limit 10")
        task_list = cursor.fetchall()
        print(task_list)
        start_list = []
        # 整理数据，并改变类目状态
        for task in task_list:
            task = {'cat_url': task[3].split('ref')[0],
                    'category_name': task[1], 'level': task[2], "category_id": task[0], 'country': task[4]}
            parmas = (task['category_id'], task['level'], task['country'])
            update_sql = f"""update amz_category set state=1 where category_id=%s and level=%s and country=%s"""
            cursor.execute(update_sql, parmas)
            # 将整理好的数据加入任务列表
            start_list.append(task)
        mysql_server.conn.commit()
        mysql_server.close()
        # 发送请求, 开始爬取
        for data in start_list:
            req_url = data['cat_url'] + 'ref='
            yield scrapy.Request(
                req_url,
                headers=self.headers,
                dont_filter=True,
                callback=self.parse,
                meta={
                    'data': data,
                    'req_url': req_url,
                    'page_num': 1,
                    # 'cookiejar': response.meta['cookiejar']
                }
            )

    def parse(self, response):
        data = response.meta.get('data')
        level = data.get('level', -2)
        categoryId = data['category_id']
        category_name = data['category_name']
        country = data['country']
        page_num = response.meta.get('page_num')
        # 由于出现验证码会302跳转改变网址，重试时无法获得正确网址，所以要保存正确网址
        req_url = response.meta.get('req_url')

        if 'exception_html' in response.url:
            # 爬取出错，进行重试
            yield scrapy.Request(url=req_url, headers=self.headers,
                                 dont_filter=True, callback=self.parse, meta=response.meta)

        else:
            if response.status == 200:
                item = {}
                item['data'] = {}
                top_list = response.xpath('//div[@id="zg-center-div"]/ol/li[@class="zg-item-immersion"]')
                num = 1
                if page_num == 2:
                    num = 51
                if top_list:
                    # 如果asin列表不为空
                    total_items = []
                    total_log_data = ''
                    for temp in top_list:
                        asin = ''
                        reviewNum = 0
                        price = '0'
                        rating = 0.0
                        notSpecified = 0
                        title = ''

                        item['data']['rank'] = num  # asin 排名
                        num += 1
                        span = temp.xpath('.//span[@class="aok-inline-block zg-item"]')

                        if span:
                            span = span[0]
                            # notSpecified = span.xpath(
                            #     './div[@class="a-row a-size-small"]/span[@class="a-size-small a-color-base"]/text()').extract_first()
                            # if notSpecified == 'Not Specified':
                            #     notSpecified = 1
                            #     # item['data']['notSpecified'] = 1
                            # else:
                            #     notSpecified = 0
                            #     # item['data']['notSpecified'] = 0

                            listingUrl = span.xpath('./a/@href').extract_first()  # 提取商品链接
                            asin = re.findall('/dp/(.*)/ref=', listingUrl)[0]  # 提取asin
                            item['data']['asin'] = asin
                            title = span.xpath('./a/div/text()').extract_first()  # 提取标题
                            if title:
                                title = title.replace('\n', ' ').strip()
                                item['data']['title'] = title
                            else:
                                title = ''
                                item['data']['title'] = ''

                            try:
                                # 提取星级
                                star = span.xpath(
                                    './div[@class="a-icon-row a-spacing-none"]/a/@title').extract_first().split(
                                    ' ')[0].replace(',', '.').replace('つ星のうち', '')
                            except:
                                star = '0'
                            rating = float(star)
                            # item['data']['rating'] = rating

                            try:
                                # 提取评论数
                                reviewNum = span.xpath(
                                    './div[@class="a-icon-row a-spacing-none"]/a[@class="a-size-small a-link-normal"]/text()').extract_first()
                            except:
                                reviewNum = '0'
                            if not reviewNum:
                                reviewNum = '0'
                            reviewNum = int(reviewNum.replace(',', '').replace('.', '').replace('\xa0', ''))
                            # item['data']['reviews'] = reviewNum

                            # 提取价格
                            price = span.xpath(
                                './div[@class="a-row"]/a//span[@class="p13n-sc-price"]/text()').extract_first()
                            if not price:
                                price = '0'
                            if 'Free' in price:
                                price = '0'
                            price = price.replace('$', '')
                            # item['data']['price'] = price

                        categoryName = data['category_name']
                        item['data']['categoryName'] = categoryName
                        # item['data']['father'] = data['father']
                        # item['data']['father'] = ''

                        # item['data']['time'] = time_
                        # item['data']['uid'] = f'{categoryName}_{data["category_id"]}_{num - 1}_{time_}'

                        item['data']['categoryId'] = categoryId
                        item['data']['country'] = country

                        # 数据标识符，flag=0表示为asin数据
                        item['flag'] = 0

                        line_data = f'{num - 1}, {asin} ,{reviewNum},{price},{rating},{notSpecified}|'

                        total_log_data += deepcopy(line_data)

                        total_items.append(deepcopy(item))
                        # self.count_num += 1
                        # yield item
                        # print(item, '===')

                        # else:
                        #     self.log.debug(f'{req_url} 无span.')

                    # if total_log_data:
                    #     total_log_data = total_log_data.strip('|')
                    #     type_ = 1
                    #     time_stamp_hour = self.get_timestamp()
                    # log_item = f'{type_}\t{data["category_id"]}\t{categoryName}\t{data["level"]}\t{page_num}\t{total_log_data}\t{time_stamp_hour}\t{self.serverip}\t{int(time.time())}\tus\t$'
                    # logger.debug(log_item)

                    # self.log.debug(f'cat: {categoryId}, page: {page_num} 完成. 商品数：{len(total_items)}')
                    # print(len(top_list))

                    # 提取类目名称: 首次提取的类目名称可能与实际类目名称不一致
                    if len(top_list) != 0 and page_num == 1:
                        # 提取出类目名称并进行数据更新
                        category_name_data = response.xpath('//div[@id="zg-right-col"]/h1/span/text()')
                        if len(category_name_data) != 0:
                            category_name = category_name_data.extract_first()
                            item = {}
                            item['category_name'] = category_name
                            item['category_id'] = categoryId
                            item['country'] = country
                            item['flag'] = 2
                            yield item
                        # 爬取第二页asin的列表
                        req_url = req_url + 'zg_bsnr_pg_{}?ie=UTF8&pg={}'.format(2, 2)
                        yield scrapy.Request(
                            req_url,
                            headers=self.headers,
                            dont_filter=True,
                            callback=self.parse,
                            meta={
                                'data': data,
                                'req_url': req_url,
                                'page_num': 2,
                            }
                        )
                        # 提取子类目
                        xpath_level = 1
                        while True:
                            # 先定位提取出整块侧边栏，通过迭代判断出本页面类目是哪一级，再提取其子类目
                            xpath_word = '//ul[@id="zg_browseRoot"]' + '/ul' * xpath_level + '/li/span'
                            category_ulr_list = response.xpath(xpath_word).extract()
                            if len(category_ulr_list) != 0 or xpath_level >= 10:
                                break
                            else:
                                xpath_level += 1
                        category_ulr_list = response.xpath(xpath_word + '/../../ul/li/a')
                        for category_data in category_ulr_list:
                            category_url = category_data.xpath('./@href').extract_first()
                            data = {}
                            data['country'] = country
                            data['bsr_url'] = category_url
                            data['category_id'] = category_url.split('/ref=')[0].split('/')[-1]
                            data['category_name'] = category_data.xpath('./text()').extract_first()
                            data['level'] = level + 1
                            data['parent_id'] = categoryId
                            data['flag'] = 1
                            yield data
                    else:
                        pass

                else:
                    # 出现验证码页面重试
                    captcha_flag = response.xpath('//div[@class="a-box-inner a-padding-extra-large"]')
                    if captcha_flag:
                        yield scrapy.Request(url=req_url, headers=self.headers,
                                             dont_filter=True, callback=self.parse, meta=response.meta)
                        return
                    else:
                        retry_flag = response.xpath('//ul[@id="zg_browseRoot"]')
                        if retry_flag:
                            pass
                        else:
                            yield scrapy.Request(url=req_url, headers=self.headers,
                                                 dont_filter=True, callback=self.parse, meta=response.meta)
                            return
            else:
                # 如果不是200，重试
                yield scrapy.Request(url=req_url, headers=self.headers,
                                     dont_filter=True, callback=self.parse, meta=response.meta)
                return

    def parse_api(self, response):
        # 接口调用函数，未使用
        data = response.meta.get('data')
        categoryId = data['category_id']
        page_num = response.meta.get('page_num')
        if response.status == 200:
            api_result = json.loads(response.text)
            if api_result['code'] == 0:
                pass
            else:
                pass
        else:
            pass

    def get_timestamp(self):
        # 时间戳获取函数，未使用
        now = int(time.time())
        now_arrey = time.localtime(now)
        now_str = time.strftime("%Y--%m--%d %H:%M:%S", now_arrey)
        timestr_list = now_str.split(' ')[0].split('--')
        hour = now_str.split(' ')[1].split(':')[0]
        timestr_list.append(hour)
        timestr = f"{timestr_list[0]}--{timestr_list[1]}--{timestr_list[2]}" + f" {timestr_list[3]}:00:00"
        timestamp = time.strptime(timestr, "%Y--%m--%d %H:%M:%S")
        timestamp = int(time.mktime(timestamp))
        return timestamp

    def get_host_ip(self):
        # 本地IP获取函数，未使用
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        return ip
