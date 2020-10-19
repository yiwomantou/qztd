import scrapy
from zol.items import ModelItem
from zol.mysql_server import Mysql_server


class ProductModelSpider(scrapy.Spider):
    name = 'product_model'
    allowed_domains = ['detail.zol.com.cn']

    custom_settings = {
        'RETRY_TIMES': 20,
        'RETRY_ENABLED ': True,
        'COOKIES_ENABLED': False,
        'HTTPERROR_ALLOWED_CODES': [500, 502, 503, 400, 404, 443, 415, 505],
        'ITEM_PIPELINES': {'zol.pipelines.ModelPipeline': 300},
        'DOWNLOADER_MIDDLEWARES': {
            # 'zol.middlewares.ProxyMiddleware': 399,
            'zol.middlewares.HeaderMiddleware': 400,
        },
    }

    def start_requests(self):
        mysql_server = Mysql_server()
        cursor = mysql_server.get_cursor()
        cursor.execute(f"select series_url from series where state=0 limit 100")
        task_list = cursor.fetchall()
        for task in task_list:
            params = (task[0],)
            update_sql = f"""update series set state=1 where series_url=%s"""
            cursor.execute(update_sql, params)
        mysql_server.conn.commit()
        for task in task_list:
            meta = {'series_url': task[0]}
            yield scrapy.Request(url=task[0], callback=self.parse, meta=meta, dont_filter=True)

    def parse(self, response):
        model_url = response.css('a[class="total"]::attr("href")').extract_first()
        model_url = 'http://detail.zol.com.cn{}'.format(model_url)
        meta = {
            'conf_url': model_url,
            'series_url': response.meta.get('series_url', '')
        }
        yield scrapy.Request(url=model_url, callback=self.parse_model, meta=meta, dont_filter=True)

    def parse_model(self, response):
        length = 0
        product_url = []
        product_name = []
        data_interface = []
        video_interface = []
        audio_interface = []
        other_interface = []
        card_reader = []
        item = ModelItem()
        tr_list = response.css('#seriesParamTable>tr')
        for tr in tr_list:
            title = tr.css('th::text').extract_first()
            if title == '型号':
                td_list = tr.css('td')
                length = len(td_list)
                for td in td_list:
                    name = td.css('a::text').extract_first()
                    url = 'http://detail.zol.com.cn{}'.format(td.css('a::attr("href")').extract_first())
                    product_url.append(url)
                    product_name.append(name)
            if title == '数据接口':
                td_list = tr.css('td')
                for td in td_list:
                    data_interface.append(td.css('::text').extract_first())
            if title == '视频接口':
                td_list = tr.css('td')
                for td in td_list:
                    video_interface.append(td.css('::text').extract_first())
            if title == '音频接口':
                td_list = tr.css('td')
                for td in td_list:
                    audio_interface.append(td.css('::text').extract_first())
            if title == '其它接口':
                td_list = tr.css('td')
                for td in td_list:
                    other_interface.append(td.css('::text').extract_first())
            if title == '读卡器':
                td_list = tr.css('td')
                for td in td_list:
                    card_reader.append(td.css('::text').extract_first())
        if not data_interface:
            data_interface = [''] * length
        if not video_interface:
            video_interface = [''] * length
        if not audio_interface:
            audio_interface = [''] * length
        if not other_interface:
            other_interface = [''] * length
        if not card_reader:
            card_reader = [''] * length
        for record in zip(product_url, product_name, data_interface, video_interface, audio_interface, other_interface,
                          card_reader):
            item['product_url'] = record[0]
            item['product_name'] = record[1]
            item['product_data_interface'] = record[2]
            item['product_video_interface'] = record[3]
            item['product_audio_interface'] = record[4]
            item['product_other_interface'] = record[5]
            item['product_card_reader'] = record[6]
            item['product_series_url'] = response.meta.get('series_url', '')
            item['conf_url'] = response.meta.get('conf_url', '')
            yield item
