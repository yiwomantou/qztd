# -*- coding: utf-8 -*-
import scrapy
import json
from amz_spider.tool.db.mysql_server import Mysql_server, RedisDBserver


class DetailParseSpider(scrapy.Spider):
    name = 'sorftime_parse'
    allowed_domains = ['plug.sorftime.com']
    start_urls = ['http://plug.sorftime.com']

    custom_settings = {
        "LOG_LEVEL": "ERROR",
        'RETRY_TIMES': 200,
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 10,
        'HTTPERROR_ALLOWED_CODES': [404, 503],
        'ITEM_PIPELINES': {
            'amz_spider.pipelines.SorftimePipeline': 300
        },
        # 'DOWNLOADER_MIDDLEWARES': {'amz_spider.middlewares.ProxyMiddleware': 400, },
    }
    # 各站点月份表
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

    # 各站点地址后缀
    country_site = {"de": "de", "fr": "fr", "uk": "co.uk", "jp": "co.jp", "us": "com", "it": "it", "es": "es",
                    'in': "in", 'br': 'com.br', 'au': "com.au", 'ca': "ca"}

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "https://plug.sorftime.com/FlowCircle/Index?site=02&token=VWNaT2NYdDkvMEtGdWFQclJpRHlOdz09&nodeId=computers&v=1.1.2&topnode=Y29tcHV0ZXJz&lang=zh-CN",
        }
        self.countryCodeArr = {"de": "www.amazon.de", "fr": "www.amazon.fr", "uk": "www.amazon.co.uk",
                               "jp": "www.amazon.co.jp",
                               "us": "www.amazon.com", "it": "www.amazon.it", "es": "www.amazon.es",
                               "ca": "www.amazon.ca",
                               "au": "www.amazon.com.au"}
        self.country_list = ["it"]  # ["us", "uk", "de", "fr", "it", "es", "jp"]
        r = RedisDBserver()
        self.collection = r.get_collection()

    def start_requests(self):
        # 根据站点领取任务，整理数据，改变状态发送请求
        for country in self.country_list:
            mysql_server = Mysql_server()
            cursor = mysql_server.get_cursor()
            table_name = 'amz_category'
            cursor.execute(
                f"select category_id, category_name, level, bsr_url from {table_name} where state=1 and country='{country}' and level<10 limit 10")
            task_list = cursor.fetchall()
            print(len(task_list), '=====')
            for task in task_list:
                task = {'category_id': task[0], 'category_name': task[1], 'level': task[2], 'country': country}
                parmas = (task['category_id'], task['level'])
                update_sql = f"""update {table_name} set state=2 where category_id=%s and level=%s"""
                cursor.execute(update_sql, parmas)
            mysql_server.conn.commit()
            mysql_server.close()
            for task in task_list:
                task = {'category_id': task[0], 'category_name': task[1], 'level': task[2], 'country': country,
                        'category_url': task[3]}
                # if task['level'] == 1:
                #     if country == 'us':
                #         if task['category_name'] == 'Cell Phones & Accessories':
                #             task['category_id'] = 'wireless'
                #         elif task['category_name'] == 'Electronics':
                #             task['category_id'] = 'electronics'
                #         elif task['category_name'] == 'Home & Kitchen':
                #             task['category_id'] = 'home-garden'
                #         else:
                #             task['category_id'] = '541966'
                #     elif country in ('uk', 'de', 'jp', 'es', 'fr'):
                #         if country == 'uk':
                #             if task['category_name'] == 'Electronics & Photo':
                #                 task['category_id'] = 'electronics'
                #             elif task['category_name'] == 'Home & Kitchen':
                #                 task['category_id'] = 'home-garden'
                #             else:
                #                 task['category_id'] = 'computers'
                #         if country == 'de':
                #             if task['category_name'] == 'Elektronik & Foto':
                #                 task['category_id'] = 'ce-de'
                #             else:
                #                 task['category_id'] = 'computers'
                #         if country == 'fr':
                #             if task['category_name'] == 'High-Tech':
                #                 task['category_id'] = 'electronics'
                #             else:
                #                 task['category_id'] = 'computers'
                #         if country == 'it':
                #             if task['category_name'] == 'Elettronica':
                #                 task['category_id'] = 'electronics'
                #             else:
                #                 task['category_id'] = 'computers'
                #         if country == 'es':
                #             if task['category_name'] == 'Electrónica':
                #                 task['category_id'] = 'electronics'
                #             else:
                #                 task['category_id'] = 'computers'
                #         if country == 'jp':
                #             if task['category_name'] == 'Electronics':
                #                 task['category_id'] = 'electronics'
                #             else:
                #                 task['category_id'] = 'computers'
                #     elif country in ('it',):
                #         task['category_id'] = 'pc'

                site_dict = {
                    'us': '01', 'uk': '02', 'de': '03', 'fr': '04', 'jp': '07', 'es': '08', 'it': '09',
                }
                url = f'https://plug.sorftime.com/FlowCircle/QueryProductByNodeId?site={site_dict[country]}&token=Zkg4Q1Y4VllTUytIRWhiWFNpVGx4Zz09'
                self.headers['Referer'] = url
                data = f'delive=0&ebc=0&bbx=0&NodeId={task["category_id"]}&times=0&ProductId=&Order=SaleCount&OrderType=desc'
                yield scrapy.Request(url, body=json.dumps(data), method='POST',
                                     meta={'country': task['country'], 'category_id': task['category_id'],
                                           'category_name': task['category_name'], 'category_url': task['category_url'],
                                           'level': task['level'],
                                           'retry_number': 0, 'table_name': table_name},
                                     headers=self.headers, callback=self.parse, dont_filter=True)

    def parse(self, response):
        category_name = response.meta.get('category_name')
        category_url = response.meta.get('category_url')
        category_id = response.meta.get('category_id')
        country = response.meta.get('country')
        level = response.meta.get('level')
        data_list = json.loads(response.text).get('data', [])
        for data in data_list:
            item = {}
            item['asin'] = data['ASIN']  # asin
            item['category_name'] = category_name  # 类目名称
            item['rank'] = data['nums']  # rank排名
            item['bsr_url'] = category_url  # bsr地址
            item['category_id'] = category_id  # 类目ID
            item['sales'] = data['SaleCount']  # 销量
            item['country'] = country  # 站点
            item['brand'] = data['Brand']  # 品牌
            item['SalePrice'] = data['SalePrice']  # 价格
            item['product_url'] = 'https://www.amazon.com/dp/' + item['asin']  # 产品地址
            item['level'] = level  # 类目等级
            yield item
