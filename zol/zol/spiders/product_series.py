import scrapy
from zol.items import SeriesItem


class SeriesSpider(scrapy.Spider):
    name = 'product_series'
    allowed_domains = ['detail.zol.com.cn']
    start_urls = ['http://detail.zol.com.cn/notebook_index/subcate16_list_1.html']

    custom_settings = {
        'RETRY_TIMES': 20,
        'RETRY_ENABLED ': True,
        'COOKIES_ENABLED': False,
        'HTTPERROR_ALLOWED_CODES': [500, 502, 503, 400, 404, 443, 415],
        'ITEM_PIPELINES': {'zol.pipelines.SeriesPipeline': 300},
        'DOWNLOADER_MIDDLEWARES': {'zol.middlewares.HeaderMiddleware': 400},
    }

    def parse(self, response):
        brands = response.css('#J_ParamBrand>a')
        for brand in brands:
            brand_name = brand.css('::text').extract_first()
            brand_url = 'http://detail.zol.com.cn{}'.format(brand.css('::attr("href")').extract_first())
            meta = {'brand_name': brand_name, 'brand_url': brand_url}
            yield scrapy.Request(url=brand_url, callback=self.series_parse, meta=meta, dont_filter=True)

    def series_parse(self, response):
        item = SeriesItem()
        big_series = response.css('#J_ParamItem4>a')
        for i in range(1, len(big_series) + 1):
            small_series = response.css('#J_flite_item_series{}-1>a'.format(str(i)))
            for record in small_series:
                series_name = record.css('::text').extract_first()
                series_url = 'http://detail.zol.com.cn{}'.format(record.css('::attr("href")').extract_first())
                item['brand_name'] = response.meta.get('brand_name', '')
                item['brand_url'] = response.meta.get('brand_url', '')
                item['series_name'] = series_name
                item['series_url'] = series_url
                yield item
