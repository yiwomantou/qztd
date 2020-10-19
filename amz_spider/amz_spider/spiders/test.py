import scrapy


class TestSpider(scrapy.Spider):
    name = 'test'
    allowed_domains = ['www.amazon.com']
    start_urls = ['https://www.amazon.co.jp/product-reviews/B087F188S7/ref=cm_cr_arp_d_viewopt_fmt?reviewerType=all_reviews&pageNumber=1&formatType=current_format&filterByStar=critical&language=en_US']

    custom_settings = {
        "COOKIES_ENABLED": False,
        'HTTPERROR_ALLOWED_CODES': [404, 503],
        # 'DOWNLOADER_MIDDLEWARES': {'amz_spider.middlewares.ProxyMiddleware': 400, },
    }

    def parse(self, response):
        print(response.status)
        print(response.text)