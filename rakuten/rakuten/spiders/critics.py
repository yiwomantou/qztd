import re
import scrapy
from rakuten.items import CriticsItem
from rakuten.db_server import Mysql_server


class CriticsSpider(scrapy.Spider):
    name = 'critics'
    allowed_domains = ['review.rakuten.co.jp']

    custom_settings = {
        'RETRY_TIMES': 20,
        'RETRY_ENABLED ': True,
        'COOKIES_ENABLED': False,
        'HTTPERROR_ALLOWED_CODES': [500, 502, 503, 400, 404, 443, 415, 505],
        'ITEM_PIPELINES': {'rakuten.pipelines.CriticsPipeline': 300},
        'DOWNLOADER_MIDDLEWARES': {'rakuten.middlewares.HeaderMiddleware': 400, },
    }

    def start_requests(self):
        mysql_server = Mysql_server()
        cursor = mysql_server.get_cursor()
        cursor.execute(f"select id, critic_url from reviews where state=2 limit 100")
        task_list = cursor.fetchall()
        for task in task_list:
            params = (task[0],)
            update_sql = f"""update reviews set state=3 where id=%s"""
            cursor.execute(update_sql, params)
        mysql_server.conn.commit()
        for task in task_list:
            if not task[1]:
                update_sql = f"""update reviews set state=4 where id=%s"""
                cursor.execute(update_sql, task[0])
                mysql_server.conn.commit()
                continue
            meta = {'id': task[0], 'critic_url': task[1]}
            yield scrapy.Request(url=task[1], callback=self.parse, meta=meta, dont_filter=True)

    def parse(self, response):
        product_bad_review = 0
        reviewRate_list = response.css('p[class="title"]>span')
        for reviewRate in reviewRate_list:
            rate = reviewRate.css('::text').extract_first()
            if float(rate) < 3:
                product_bad_review += 1

        next_text = response.css('p[class="pager tright"]>a:last-child::text').extract_first()
        next_url = response.css('p[class="pager tright"]>a:last-child::attr("href")').extract_first()
        if next_text == '次へ>>':
            meta = {
                'id': response.meta.get('id'),
                'critic_url': response.meta.get('critic_url'),
                'product_bad_review': product_bad_review + response.meta.get('product_bad_review', 0),
            }
            yield scrapy.Request(url=next_url, callback=self.parse, meta=meta, dont_filter=True)
        else:
            item = CriticsItem()
            temp = response.css('#mypageProfileOk>p::text').extract()[-1].split('／')
            age = temp[0].split('（')[-1]
            sex = temp[-1].split('）')[0]
            product_review = \
                response.css('p[class="pager tright"]>span:first-child::text').extract_first().split('(')[-1].split(
                    ')')[0]
            total_reviews = response.css('#reviewTotal>div>dl>dd:last-child::text').extract_first()
            item['id'] = response.meta.get('id')
            item['critic_id'] = response.meta.get('critic_url').split('/')[-3]
            item['critic_url'] = response.meta.get('critic_url')
            item['age'] = age
            item['sex'] = sex
            item['product_review'] = int(re.findall(r"\d+\.?\d*|$", product_review)[0] or 0)
            item['store_reviews'] = int(re.findall(r"\d+\.?\d*|$", total_reviews)[0] or 0) - item['product_review']
            item['product_bad_review'] = product_bad_review + response.meta.get('product_bad_review', 0)
            yield item
