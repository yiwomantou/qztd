import scrapy
from datetime import datetime
from rakuten.items import ShopReviewsItem


class ShopReviewsSpider(scrapy.Spider):
    name = 'shop_reviews'
    allowed_domains = ['review.rakuten.co.jp']

    custom_settings = {
        'RETRY_TIMES': 20,
        'RETRY_ENABLED ': True,
        'COOKIES_ENABLED': False,
        'ITEM_PIPELINES': {'rakuten.pipelines.ShopReviewsPipeline': 300, },
        'DOWNLOADER_MIDDLEWARES': {'rakuten.middlewares.HeaderMiddleware': 300, },
        'HTTPERROR_ALLOWED_CODES': [500, 502, 503, 400, 404, 443, 415, 505],
    }

    def start_requests(self):
        start_urls = 'https://review.rakuten.co.jp/shop/4/368316_368316/1.1/'
        yield scrapy.Request(url=start_urls, callback=self.parse, dont_filter=True)

    def parse(self, response):
        item = ShopReviewsItem()
        revRvwUserSec = response.css('div[class="revRvwUserSec hreview"]')
        for rev in revRvwUserSec:
            product_id = ''
            product_name = ''
            review_type = 'ショップレビュー'
            product = rev.css('p[class="revUserItemImg"]')
            if product:
                # 有的商品已下架没有链接
                if product.css('a::attr(href)').extract_first():
                    review_type = '商品レビュー'
                    product_name = product.css('a>img::attr(alt)').extract_first()
                    product_id = product.css('a::attr(href)').extract_first().split('/')[-2]
            review_time = rev.css('span[class="revUserEntryDate dtreviewed"]::text').extract_first()
            review_raiting = rev.css('span[class="revUserRvwerNum value"]::text').extract_first()
            review_title = rev.css('dt[class="revRvwUserEntryTtl summary"]::text').extract_first()
            review_body = rev.css('dd[class="revRvwUserEntryCmt description"]::text').extract()
            review_detail_url = rev.css('a[l2id_linkname="body_05"]::attr(href)').extract_first()
            item['review_type'] = review_type
            item['product_name'] = product_name
            item['product_id'] = product_id
            item['review_detail_url'] = review_detail_url
            item['review_raiting'] = float(review_raiting)
            item['review_time'] = datetime.strptime(review_time.replace('-', '/'), '%Y/%m/%d')
            item['review_title'] = review_title
            item['review_body'] = ''.join(list(map(str.strip, review_body)))
            yield item
        next_text = response.css('div[class="revPagination"]>a:last-child::text').extract_first()
        next_url = response.css('div[class="revPagination"]>a:last-child::attr(href)').extract_first()
        if next_text == '次の15件 >>':
            yield scrapy.Request(url=next_url, callback=self.parse, dont_filter=True)
