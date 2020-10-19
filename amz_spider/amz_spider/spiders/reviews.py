# -*- coding: utf-8 -*-
import scrapy
import time
import re
from amz_spider.tool.db.mysql_server import Mysql_server, RedisDBserver
import json


class ReviewsSpider(scrapy.Spider):
    name = 'reviews'
    allowed_domains = ['www.amazon.com']
    start_urls = ['http://www.amazon.com/']
    custom_settings = {
        # 'LOG_LEVEL': 'ERROR',
        'RETRY_TIMES': 200,
        'HTTPERROR_ALLOWED_CODES': [404, 503],
        'ITEM_PIPELINES': {
            'amz_spider.pipelines.AmzReviewsPipeline': 300
        },
        'DOWNLOADER_MIDDLEWARES': {
            # 'amz_spider.middlewares.ProxyMiddleware': 400,
        },
    }

    # 各站点月份数据
    us_month = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                "November", "December"]
    fr_month = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre",
                "novembre", "décembre"]
    de_month = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober",
                "November", "Dezember"]
    es_month = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
                "noviembre", "diciembre"]
    it_month = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre",
                "ottobre", "novembre", "dicembre"]

    def __init__(self):
        # redis服务
        r = RedisDBserver()
        self.collection = r.get_collection()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
        }
        # 站点列表
        self.country_list = ["us", "de"]  # ["us", "uk", "de", "fr", "it", "es", "jp"]
        self.task_type = 0
        # 各站点地址
        self.countryCodeArr = {"de": "www.amazon.de", "fr": "www.amazon.fr", "uk": "www.amazon.co.uk",
                               "jp": "www.amazon.co.jp",
                               "us": "www.amazon.com", "it": "www.amazon.it", "es": "www.amazon.es",
                               "ca": "www.amazon.ca",
                               "au": "www.amazon.com.au"}

    def start_requests(self):
        # 取出任务并改变状态
        for country in self.country_list:
            mysql_server = Mysql_server()
            cursor = mysql_server.get_cursor()
            table_name = country + "_asins"
            cursor.execute(f"select distinct(asin) from {table_name} where state=5")
            task_list = cursor.fetchall()
            print(task_list)
            # task_list = (("B0753H1Z7L",),)  # 测试用例
            for task in task_list:
                task = {'asin': task[0], 'countrycode': country}
                parmas = (task['asin'],)
                update_sql = f"""update {table_name} set state=6 where asin=%s"""
                cursor.execute(update_sql, parmas)
            mysql_server.conn.commit()
            mysql_server.conn.close()
            for task in task_list:
                task = {'asin': task[0], 'countrycode': country}
                page_num = 1
                url = f'https://{self.countryCodeArr[task["countrycode"]]}/product-reviews/{task["asin"]}/ref=cm_cr_arp_d_viewopt_fmt?reviewerType=all_reviews&pageNumber={page_num}&formatType=current_format&filterByStar=critical&language=en_US'
                if self.task_type == 1:
                    url = f'https://{self.countryCodeArr[task["countrycode"]]}/product-reviews/{task["asin"]}?reviewerType=all_reviews&pageNumber={page_num}#reviews-filter-bar&language=en_US'
                yield scrapy.Request(
                    url=url,
                    headers=self.headers,
                    meta={
                        'page_num': page_num,
                        'countrycode': task['countrycode'],
                        'asin': task['asin'],
                        'table_name': table_name},
                    callback=self.parse,
                    dont_filter=True
                )

    def parse(self, response):
        # 代理状态更新, 如果代理可用，则给一个高分数令其至前，否则给一个低分数置后
        proxy = response.meta.get('proxy', '').replace('https://', '').replace('http://', '')
        proxy_data = {"proxy": proxy,
                      "fail_count": 0, "region": "", "type": "",
                      "source": "spider",
                      "check_count": 20, "last_status": 0,
                      "last_time": ""}
        page_num = response.meta['page_num']
        table_name = response.meta['table_name']
        asin = response.meta['asin']
        countrycode = response.meta['countrycode']
        # 判断是否出现验证码，否则重试并改变代理状态
        if len(response.body) < 10000 or response.status == 503:
            proxy_data['fail_count'] = 18
            self.collection.hset(name="useful_proxy", key=proxy, value=json.dumps(proxy_data))
            yield scrapy.Request(url=response.url,
                                 headers=self.headers,
                                 meta={
                                     'page_num': page_num,
                                     'asin': asin,
                                     'table_name': table_name,
                                     'countrycode': countrycode},
                                 callback=self.parse,
                                 dont_filter=True
                                 )
            return
        elif response.status == 404:
            # 若asin不存在则直接停止爬取    # Todo: 识别后应该进行状态重新设置标记
            return
        self.collection.hset(name="useful_proxy", key=proxy, value=json.dumps(proxy_data))

        # 提取评论列表
        data_list = response.xpath('//div[@id="cm_cr-review_list"]/div')
        if len(data_list) > 0:
            for data in data_list:
                item = {}
                item['reviewID'] = data.xpath('./@id').extract_first()  # 评论ID
                try:
                    # 评论人ID
                    item['profileID'] = \
                        data.xpath('./div/div/div//a[@class="a-profile"]/@href').extract_first().split('.')[2].split(
                            '/')[0]
                except:
                    continue

                # 评论时间
                item['review_time'] = data.xpath(
                    './div/div/span[@data-hook="review-date"]/text()').extract_first()  # .split('on ')[-1]
                # 评论评分
                item['review_raiting'] = float(
                    data.xpath('.//div/div/div/a/@title').extract_first().split(' ')[0].replace(',', '.'))
                # 评论标题
                item['review_title'] = data.xpath(
                    './/div/div//a[@data-hook="review-title"]/span/text()').extract_first()
                if item['review_title'] == None:
                    item['review_title'] = ""
                # 评论内容
                item['review_body'] = data.xpath('string(.//span[@data-hook="review-body"]/span)').extract_first()
                # 评论有用数
                helpful_str = data.xpath('./div/div/div/div/span/div/span/text()').extract_first()
                if helpful_str is None:
                    item['helpful_num'] = 0
                elif helpful_str.startswith('One') or helpful_str.startswith('Une') or helpful_str.startswith(
                        'A una') or helpful_str.startswith('Una') or helpful_str.startswith('Eine'):
                    item['helpful_num'] = 1
                else:
                    try:
                        item['helpful_num'] = int(helpful_str.split(' ')[1].replace(',', ''))
                    except:
                        item['helpful_num'] = int(helpful_str.split(' ')[0].replace(',', ''))
                    # item['helpful_num'] = helpful_str

                # 评论是否为VP评论
                vp_str = data.xpath('./div/div/div/span/a/span/text()').extract_first()
                if vp_str in ['Verified Purchase', 'Verifizierter Kauf', 'Amazonで購入',
                              'Achat vérifié', 'Acquisto verificato', 'Compra verificada', '']:
                    item['is_VP'] = 1  # 是VP评论
                elif vp_str is None:
                    item['is_VP'] = 0  # 不是VP评论
                else:
                    item['is_VP'] = 2  # 其他情况，比如早期评论计划评论
                # ------------------------------时间处理-----------------------------------
                review_time = item['review_time']
                # 时间处理
                if review_time != '':
                    if countrycode == 'us' or countrycode == 'ca' or countrycode == 'jp':
                        review_time = review_time.split('on ')[-1]
                        review_time = time.strftime("%Y-%m-%d", time.strptime(review_time, "%B %d, %Y"))
                    elif countrycode == 'fr':
                        fr_month = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
                                    "septembre", "octobre", "novembre", "décembre"]
                        review_time = review_time.split('le ')[-1]  # .decode('utf-8').encode("latin-1")
                        for each in range(12):
                            if self.fr_month[each] in review_time:
                                review_time = review_time.replace(self.fr_month[each], self.us_month[each])
                                break
                        review_time = time.strftime("%Y-%m-%d", time.strptime(review_time, "%d %B %Y"))
                    elif countrycode == 'de':
                        de_month = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September",
                                    "Oktober", "November", "Dezember"]
                        review_time = review_time.split('vom ')[-1]  # .decode('utf-8').encode("latin-1")
                        for each in range(12):
                            if self.de_month[each] in review_time:
                                review_time = review_time.replace(self.de_month[each], self.us_month[each])
                                break
                        review_time = time.strftime("%Y-%m-%d", time.strptime(review_time, "%d. %B %Y"))
                    elif countrycode == 'es':
                        self.es_month = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
                                         "septiembre", "octubre", "noviembre", "diciembre"]
                        review_time = review_time.split('el ')[-1].replace('de ',
                                                                           '')  # .decode('utf-8').encode("latin-1")
                        for each in range(12):
                            if self.es_month[each] in review_time:
                                review_time = review_time.replace(self.es_month[each], self.us_month[each])
                                break
                        review_time = time.strftime("%Y-%m-%d", time.strptime(review_time, "%d %B %Y"))
                    elif countrycode == 'it':
                        it_month = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto",
                                    "settembre", "ottobre", "novembre", "dicembre"]
                        review_time = review_time.split('il ')[-1]  # .decode('utf-8').encode("latin-1")
                        for each in range(12):
                            if self.it_month[each] in review_time:
                                review_time = review_time.replace(self.it_month[each], self.us_month[each])
                                break
                        review_time = time.strftime("%Y-%m-%d", time.strptime(review_time, "%d %B %Y"))
                    # elif countrycode == 'jp':
                    #     review_time = '-'.join(re.findall('\d+', review_time))
                    #     review_time = time.strftime("%Y-%m-%d", time.strptime(review_time, "%Y-%m-%d"))
                    elif countrycode == 'uk' or countrycode == 'au':
                        review_time = review_time.split('on ')[-1]
                        review_time = time.strftime("%Y-%m-%d", time.strptime(review_time, "%d %B %Y"))
                item['review_time'] = review_time
                item['asin'] = asin
                item['country'] = countrycode
                # ------------------------------时间处理-----------------------------------
                yield item

        try:
            if len(data_list) >= 10 and page_num == 1:
                # 提取出评论总数之后进行并发爬取
                if countrycode == 'fr':
                    reviews_count = \
                        response.xpath('//div[@id="filter-info-section"]/span/text()').extract_first().replace(',', '')
                    reviews_count = re.findall('sur ([0-9]+)', reviews_count)[0]
                elif countrycode == 'it':
                    reviews_count = \
                        response.xpath('//div[@id="filter-info-section"]/span/text()').extract_first().replace(',', '')
                    # print(reviews_count, '------')
                    reviews_count = re.findall('su ([0-9]+)', reviews_count)[0]
                elif countrycode == 'de':  # or countrycode == 'uk':
                    reviews_count = \
                        response.xpath('//div[@id="filter-info-section"]/span/text()').extract_first().replace(',', '')
                    # print(reviews_count, '------')
                    reviews_count = re.findall('von ([0-9]+)', reviews_count)[0]
                elif countrycode == 'uk':
                    reviews_count = \
                        response.xpath('//div[@id="filter-info-section"]/span/text()').extract_first().replace(',', '')
                    # print(reviews_count, '------')
                    reviews_count = re.findall('of ([0-9]+)', reviews_count)[0]
                elif countrycode == 'es':
                    reviews_count = \
                        response.xpath('//div[@id="filter-info-section"]/span/text()').extract_first().replace(',', '')
                    # print(reviews_count, '------')
                    reviews_count = re.findall('de ([0-9]+)', reviews_count)[0]
                else:
                    reviews_count = \
                        response.xpath('//div[@id="filter-info-section"]/span/text()').extract_first().split(' ')[
                            -2].replace(
                            ',', '')
        except:
            reviews_count = \
                response.xpath('//div[@id="filter-info-section"]//span/text()').extract()
            if reviews_count != []:
                reviews_count = re.findall('\| (.*?) ', reviews_count[-1])[0]
                reviews_count = reviews_count.replace(',', '').replace('.', '').replace(' ', '')
            else:
                reviews_count = 0

            page_count = int(reviews_count) // 10 + 2  # 10条一页，对10取余加2保证完全爬取
            for page_num in range(2, page_count):
                url = f'https://{self.countryCodeArr[countrycode]}/product-reviews/{asin}/ref=cm_cr_arp_d_viewopt_fmt?reviewerType=all_reviews&pageNumber={page_num}&formatType=current_format&filterByStar=critical&language=en_US'
                if self.task_type == 1:
                    url = f'https://{self.countryCodeArr[countrycode]}/product-reviews/{asin}?reviewerType=all_reviews&pageNumber={page_num}#reviews-filter-bar&language=en_US'
                yield scrapy.Request(
                    url=url,
                    headers=self.headers,
                    meta={
                        'page_num': page_num,
                        'asin': asin,
                        'countrycode': countrycode,
                        "table_name": table_name},
                    callback=self.parse,
                    dont_filter=True
                )
            mysql_server = Mysql_server()
            cursor = mysql_server.get_cursor()
            parmas = (asin,)
            # 并行爬取开始后改变状态表示已爬取，并不关心什么时候完成爬取
            update_sql = f"""update {table_name} set state=7 where asin=%s"""
            cursor.execute(update_sql, parmas)
            mysql_server.conn.commit()
            mysql_server.close()
