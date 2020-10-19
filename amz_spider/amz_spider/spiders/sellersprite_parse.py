# -*- coding: utf-8 -*-
import requests
import scrapy
import json
import time
from amz_spider.tool.db.mysql_server import Mysql_server
import time, datetime


class SellerspriteParseSpider(scrapy.Spider):
    name = 'sellersprite_parse'
    allowed_domains = ['www.sellersprite', "www.baidu.com"]
    start_urls = ["https://www.sellersprite.com"]
    custom_settings = {
        # "LOG_LEVEL": "ERROR",
        'RETRY_TIMES': 20,
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS': 1,
        'HTTPERROR_ALLOWED_CODES': [404, 503, 302, 301, 400],
        'REDIRECT_ENABLED': False,
        'ITEM_PIPELINES': {
            'amz_spider.pipelines.SellerspritePipeline': 300
        },
    }

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "cache-control": "max-age=0"
        }

        # 账号cookies
        cookie_list = {
            '16532819720': [
                {"domain": ".sellersprite.com", "expirationDate": 1658633168, "hostOnly": False, "httpOnly": False,
                 "name": "_ga", "path": "/", "sameSite": "unspecified", "secure": False, "session": False,
                 "storeId": "0", "value": "GA1.2.2076145104.1595560854", "id": 1},
                {"domain": ".sellersprite.com", "expirationDate": 1595561228, "hostOnly": False, "httpOnly": False,
                 "name": "_gat_gtag_UA_135032196_1", "path": "/", "sameSite": "unspecified", "secure": False,
                 "session": False, "storeId": "0", "value": "1", "id": 2},
                {"domain": ".sellersprite.com", "expirationDate": 1595647568, "hostOnly": False, "httpOnly": False,
                 "name": "_gid", "path": "/", "sameSite": "unspecified", "secure": False, "session": False,
                 "storeId": "0", "value": "GA1.2.793433934.1595560854", "id": 3},
                {"domain": ".sellersprite.com", "expirationDate": 1611329170, "hostOnly": False, "httpOnly": False,
                 "name": "crisp-client%2Fsession%2F02ce6ae3-e1ab-4bb7-ae11-b1a839c52e78", "path": "/",
                 "sameSite": "lax", "secure": False, "session": False, "storeId": "0",
                 "value": "session_fc5d167a-d474-4fa0-b2bd-cd7b2c4355f9", "id": 4},
                {"domain": ".sellersprite.com", "expirationDate": 1611113167.173862, "hostOnly": False,
                 "httpOnly": False, "name": "ecookie", "path": "/", "sameSite": "unspecified", "secure": False,
                 "session": False, "storeId": "0", "value": "Pz2ecLEpt1bwi1AE_CN", "id": 5},
                {"domain": "www.sellersprite.com", "expirationDate": 3743044813.50212, "hostOnly": False,
                 "httpOnly": False, "name": "ao_lo_to_n", "path": "/", "sameSite": "unspecified", "secure": False,
                 "session": False, "storeId": "0",
                 "value": "\"5699855951IrZXNTSoIlHhPKyHGfg/7Y44DjU/uf1zExsGffLvK1ezZe9o9CYFxUCBufJ08CQhh/C8Ihl3wxiKKwX5+hKoyEbWnaiWWIKpqrrTbD+ENVA=\"",
                 "id": 6},
                {"domain": "www.sellersprite.com", "expirationDate": 1595561770, "hostOnly": False, "httpOnly": False,
                 "name": "crisp-client%2Fsocket%2F02ce6ae3-e1ab-4bb7-ae11-b1a839c52e78", "path": "/", "sameSite": "lax",
                 "secure": False, "session": False, "storeId": "0", "value": "0", "id": 7},
                {"domain": "www.sellersprite.com", "hostOnly": False, "httpOnly": False, "name": "JSESSIONID",
                 "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0",
                 "value": "12F5F6542A83AED268D17EF58CB3C5FD", "id": 8},
                {"domain": "www.sellersprite.com", "expirationDate": 1611112831.445373, "hostOnly": False,
                 "httpOnly": False, "name": "rank_c_s_ind", "path": "/", "sameSite": "unspecified", "secure": False,
                 "session": False, "storeId": "0", "value": "1", "id": 9},
                {"domain": "www.sellersprite.com", "hostOnly": False, "httpOnly": False, "name": "rank-login-user",
                 "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0",
                 "value": "5699855951IrZXNTSoIlHhPKyHGfg/7TMbw6xY7YpCjminsqgfQO0nIbvgbLEN8THIHs94HSLc", "id": 10}]
        }
        self.cookies = {i['name']: i['value'] for i in cookie_list[
            '16532819720']}

        # 各站点代号
        self.countryCode = {"us": "1", "jp": "2", "uk": "3", "de": "4", "fr": "5", "it": "6", "es": "7", "ca": "8"
                            }
        # 任务站点列表
        self.country_list = ["fr"]  # ["us", "uk", "de", "fr", "it", "es", "jp"]

    def start_requests(self):
        # 提取asin，整理数据发送请求, 改变状态
        for country in self.country_list:
            mysql_server = Mysql_server()
            cursor = mysql_server.get_cursor()
            table_name = country + '_asins'
            cursor.execute(f"select asin from {table_name} where state=2 limit 100")
            task_list = cursor.fetchall()
            print(task_list)
            for task in task_list:
                task = {'asin': task[0], 'country': country}
                parmas = (task['asin'],)
                update_sql = f"""update {table_name} set state=3 where asin=%s"""
                cursor.execute(update_sql, parmas)
            mysql_server.conn.commit()
            mysql_server.close()
            for task in task_list:
                task = {'asin': task[0], 'country': country}
                if len(task['asin']) > 10 and '?' in task['asin']:
                    asin = task['asin'].split('/')[-1].split('?')[0]
                    if len(asin) == 10:
                        asin = asin.upper()
                elif len(task['asin']) == 10:
                    asin = task['asin'].upper()
                item = {}
                item['asin'] = task['asin']
                item['country'] = country
                item['table_name'] = table_name
                item['total_dict'] = {}
                item['rankHistory'] = {}
                # 站点后缀对应表
                code_dir = {
                    "us": "COM",
                    "uk": "CO_UK",
                    "de": "DE",
                    "fr": "FR",
                    "it": "IT",
                    'es': "ES",
                    'jp': "CO_JP"
                }
                url = f"https://www.amzscout.net/extensions/scoutpro/v1/products/{code_dir[country]}"
                # 各站点账号cookie请求头
                headers = {'us': {
                    "Host": "amzscout.net",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36",
                    "x-instance-id": "a3fa3f86-9edd-4743-90f6-26dace59202b",
                    "x-signature": "5bb36a25caf0e17720e9a4a9e5cfa3ff",
                    "Cookie": "_ga=GA1.2.1638731990.1595486255; _gid=GA1.2.1082995224.1595486255; mindboxDeviceUUID=7a11484f-1338-47a3-863e-747203d8f968; directCrm-session=%7B%22deviceGuid%22%3A%227a11484f-1338-47a3-863e-747203d8f968%22%7D; cid=19907047; G_ENABLED_IDPS=google; h=AJ8zGal7cqMwMFWwJ1JS",
                    "Content-Type": "application/json",
                    "Accept": "*/*",
                    "Cache-Control": "no-cache",
                    "Postman-Token": "e21cd0f2-623c-4d26-9101-61e784be19f3",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    "Content-Length": "23", },
                    'uk': {
                        "Host": "amzscout.net",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36",
                        "x-instance-id": "a3fa3f86-9edd-4743-90f6-26dace59202b",
                        "x-signature": "8fad7d23e214780b9b8a5bf6e1c36887",
                        "Cookie": "_ga=GA1.2.1638731990.1595486255; _gid=GA1.2.1082995224.1595486255; mindboxDeviceUUID=7a11484f-1338-47a3-863e-747203d8f968; directCrm-session=%7B%22deviceGuid%22%3A%227a11484f-1338-47a3-863e-747203d8f968%22%7D; cid=19907047; G_ENABLED_IDPS=google; h=AJ8zGal7cqMwMFWwJ1JS",
                        "Content-Type": "application/json",
                        "Accept": "*/*",
                        "Cache-Control": "no-cache",
                        "Postman-Token": "e21cd0f2-623c-4d26-9101-61e784be19f3",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Connection": "keep-alive",
                        "Content-Length": "23", },
                    'de': {
                        "Host": "amzscout.net",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36",
                        "x-instance-id": "a3fa3f86-9edd-4743-90f6-26dace59202b",
                        "x-signature": "7c0e3563c17a8dad639895474b4c8c9c",
                        "Cookie": "_ga=GA1.2.1638731990.1595486255; directCrm-session=%7B%22deviceGuid%22%3A%227a11484f-1338-47a3-863e-747203d8f968%22%7D; mindboxDeviceUUID=7a11484f-1338-47a3-863e-747203d8f968; cid=19907047; G_ENABLED_IDPS=google; h=AJ8zGal7cqMwMFWwJ1JS; _ym_uid=1595493952224708321; _ym_d=1595493952; _gid=GA1.2.1387564678.1595814486",
                        "Content-Type": "application/json",
                        "Accept": "*/*",
                        "Cache-Control": "no-cache",
                        "Postman-Token": "e21cd0f2-623c-4d26-9101-61e784be19f3",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Connection": "keep-alive",
                        "Content-Length": "23", },
                    'fr': {
                        "Host": "amzscout.net",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36",
                        "x-instance-id": "a3fa3f86-9edd-4743-90f6-26dace59202b",
                        "x-signature": "68b2abf9af33e951fecdf240fe897b1d",
                        "Cookie": "_ga=GA1.2.1638731990.1595486255; directCrm-session=%7B%22deviceGuid%22%3A%227a11484f-1338-47a3-863e-747203d8f968%22%7D; mindboxDeviceUUID=7a11484f-1338-47a3-863e-747203d8f968; cid=19907047; G_ENABLED_IDPS=google; h=AJ8zGal7cqMwMFWwJ1JS; _ym_uid=1595493952224708321; _ym_d=1595493952; _gid=GA1.2.1387564678.1595814486",
                        "Content-Type": "application/json",
                        "Accept": "*/*",
                        "Cache-Control": "no-cache",
                        "Postman-Token": "e21cd0f2-623c-4d26-9101-61e784be19f3",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Connection": "keep-alive",
                        "Content-Length": "23", },
                    'it': {
                        "Host": "amzscout.net",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36",
                        "x-instance-id": "a3fa3f86-9edd-4743-90f6-26dace59202b",
                        "x-signature": "54be64e0f25f50ffa05638afbf6811a3",
                        "Cookie": "_ga=GA1.2.1638731990.1595486255; directCrm-session=%7B%22deviceGuid%22%3A%227a11484f-1338-47a3-863e-747203d8f968%22%7D; mindboxDeviceUUID=7a11484f-1338-47a3-863e-747203d8f968; cid=19907047; G_ENABLED_IDPS=google; h=AJ8zGal7cqMwMFWwJ1JS; _ym_uid=1595493952224708321; _ym_d=1595493952; _gid=GA1.2.1387564678.1595814486",
                        "Content-Type": "application/json",
                        "Accept": "*/*",
                        "Cache-Control": "no-cache",
                        "Postman-Token": "e21cd0f2-623c-4d26-9101-61e784be19f3",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Connection": "keep-alive",
                        "Content-Length": "23", },
                    'es': {
                        "Host": "amzscout.net",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36",
                        "x-instance-id": "a3fa3f86-9edd-4743-90f6-26dace59202b",
                        "x-signature": "dbb302cf60e8efa77bc33e596a24b6b2",
                        "Cookie": "_ga=GA1.2.1638731990.1595486255; directCrm-session=%7B%22deviceGuid%22%3A%227a11484f-1338-47a3-863e-747203d8f968%22%7D; mindboxDeviceUUID=7a11484f-1338-47a3-863e-747203d8f968; cid=19907047; G_ENABLED_IDPS=google; h=AJ8zGal7cqMwMFWwJ1JS; _ym_uid=1595493952224708321; _ym_d=1595493952; _gid=GA1.2.114546357.1596414342",
                        "Content-Type": "application/json",
                        "Accept": "*/*",
                        "Cache-Control": "no-cache",
                        "Postman-Token": "e21cd0f2-623c-4d26-9101-61e784be19f3",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Connection": "keep-alive",
                        "Content-Length": "23", },
                    'jp': {
                        "Host": "amzscout.net",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36",
                        "x-instance-id": "8e86ea27-d5fa-4f8c-b347-96a659338078",
                        "x-signature": "7615fd3657994cba7e376594101849ab",
                        "Cookie": "cid=20212472; mindboxDeviceUUID=486b8129-af83-42e9-a5cf-b70776d8b1e6; directCrm-session=%7B%22deviceGuid%22%3A%22486b8129-af83-42e9-a5cf-b70776d8b1e6%22%7D; h=bgXLkUopN26n8fEvlgHn",
                        "Content-Type": "application/json",
                        "Accept": "*/*",
                        "Cache-Control": "no-cache",
                        "Postman-Token": "e21cd0f2-623c-4d26-9101-61e784be19f3",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Connection": "keep-alive",
                        "Content-Length": "23", },
                }
                post = [{"asin": task['asin']}]  # {
                # 该post请求用scrapy无法实现，所以用request实现数据获取，再通过多访问一次baidu走scrapy的流程返回数据
                # Todo: 优化实现用scrapy实现请求
                while True:
                    # 代理可能失效，循环至成功为止
                    try:
                        response = requests.post(url, data=json.dumps(post), headers=headers[country], timeout=10,
                                                 verify=False)
                        chartData = json.loads(response.text)
                        # 提取近一年销量和排名数据，但是保存时无指定情况则只保存一条数据
                        if len(chartData) > 0:
                            item['total_dict']['2020-10'] = chartData[0].get('estSales', 0)
                            salesHistory = chartData[0].get('salesHistory', [])
                            time_int = int(time.time())
                            salesHistory.reverse()
                            # 提取历史销量数据
                            for saledata in salesHistory:
                                time_int -= 86400
                                if saledata is not None:
                                    timeArray = time.localtime(time_int)
                                    time_str = time.strftime("%Y-%m-%d", timeArray)
                                    item['total_dict'][time_str] = saledata
                            rankHistory = chartData[0].get('rankHistory', [])
                            rankHistory.reverse()
                            time_int = int(time.time())
                            # 提取历史排名数据
                            for rankdata in rankHistory:
                                time_int -= 86400
                                if rankdata is not None:
                                    timeArray = time.localtime(time_int)
                                    time_str = time.strftime("%Y-%m-%d", timeArray)
                                    item['rankHistory'][time_str] = rankdata
                        else:
                            item['total_dict']['2020-10'] = 0
                        break
                    except:
                        time.sleep(3)
                        pass
                url = 'https://www.baidu.com'
                yield scrapy.Request(url, method='get',  # body=json.dumps(post),
                                     meta={'country': country, 'asin': task['asin'],
                                           'retry_number': 0, 'table_name': table_name,
                                           "item": item},
                                     headers=headers, callback=self.parse_total, dont_filter=True, )

    def parse(self, response):
        country = response.meta['country']
        asin = response.meta['asin']
        table_name = response.meta['table_name']
        if response.status in [302, 301]:
            time.sleep(5)
            yield scrapy.Request(url=response.url, meta={'country': country, 'asin': asin,
                                                         'retry_number': 0, 'table_name': table_name},
                                 headers=self.headers, callback=self.parse, dont_filter=True, cookies=self.cookies)
            return
        data_list = json.loads(response.body).get('data', [])
        item = {}
        result_list = []
        for data in data_list:
            result = {}
            result['keyword'] = data['keyword']
            for months, searches in zip(data['months'][-6:], data['searches'][-6:]):
                result[months] = searches
            result_list.append(result)
        item['keyword_list'] = result_list
        item['asin'] = asin
        item['country'] = country
        item['table_name'] = table_name
        code_dir = {
            "us": "COM",
            "uk": "CO_UK",
        }
        url = f"https://www.amzscout.net/extensions/scoutpro/v1/products/{code_dir[country]}"
        post_data = [{"asin": "%s" % asin}]  # {
        headers = {
            "Host": "amzscout.net",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36",
            "x-instance-id": "a3fa3f86-9edd-4743-90f6-26dace59202b",
            "x-signature": "8fad7d23e214780b9b8a5bf6e1c36887",
            "Cookie": "_ga=GA1.2.1638731990.1595486255; _gid=GA1.2.1082995224.1595486255; mindboxDeviceUUID=7a11484f-1338-47a3-863e-747203d8f968; directCrm-session=%7B%22deviceGuid%22%3A%227a11484f-1338-47a3-863e-747203d8f968%22%7D; cid=19907047; G_ENABLED_IDPS=google; h=AJ8zGal7cqMwMFWwJ1JS",
            "Content-Type": "application/json",
        }
        item['total_dict'] = {}
        yield scrapy.FormRequest(url, formdata=json.dumps(post_data), meta={'country': country, 'asin': asin,
                                                                            'retry_number': 0, 'table_name': table_name,
                                                                            "item": item},
                                 headers=headers, callback=self.parse_total, dont_filter=True,
                                 cookies=self.cookies)

    def parse_total(self, response):
        country = response.meta['country']
        asin = response.meta['asin']
        item = response.meta['item']
        item['total_dict']['2020-10'] = 0 if item['total_dict'].get('2020-10', 0) == 0 else item['total_dict'][
            '2020-10']
        item['keyword_list'] = []
        yield item
