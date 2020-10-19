import scrapy
from datetime import datetime
from rakuten.items import ReviewsItem


class ReviewsSpider(scrapy.Spider):
    name = 'reviews'
    allowed_domains = ['review.rakuten.co.jp']

    custom_settings = {
        'RETRY_TIMES': 20,
        'RETRY_ENABLED ': True,
        'COOKIES_ENABLED': False,
        'ITEM_PIPELINES': {'rakuten.pipelines.ReviewsPipeline': 300, },
        'DOWNLOADER_MIDDLEWARES': {'rakuten.middlewares.HeaderMiddleware': 300, },
        'HTTPERROR_ALLOWED_CODES': [500, 502, 503, 400, 404, 443, 415, 505],
    }

    def start_requests(self):
        start_urls = 'https://review.rakuten.co.jp/item/1/338493_10000159/1.1/'
        meta = {'review_url': start_urls}
        yield scrapy.Request(url=start_urls, meta=meta, callback=self.parse, dont_filter=True)

    def parse(self, response):
        item = ReviewsItem()
        product_url = response.css('a[sid_linkname="item_01"]::attr(href)').extract_first()
        revRvwUserSec = response.css('div[class="revRvwUserSec hreview"]')
        for rev in revRvwUserSec:
            review_time = rev.css('span[class="revUserEntryDate dtreviewed"]::text').extract_first()
            review_raiting = rev.css('span[class="revUserRvwerNum value"]::text').extract_first()
            review_title = rev.css('dt[class="revRvwUserEntryTtl summary"]::text').extract_first()
            review_body = rev.css('dd[class="revRvwUserEntryCmt description"]::text').extract()
            critic_url = rev.css('li[class="revUserFace"]>a::attr("href")').extract_first()
            item['product_url'] = product_url
            item['review_url'] = response.meta.get('review_url')
            item['review_time'] = datetime.strptime(review_time.replace('-', '/'), '%Y/%m/%d')
            item['review_raiting'] = float(review_raiting)
            item['review_title'] = review_title or ''
            item['review_body'] = ''.join(list(map(str.strip, review_body)))
            item['critic_url'] = critic_url or ''
            yield item
        next_text = response.css('div[class="revPagination"]>a:last-child::text').extract_first()
        next_url = response.css('div[class="revPagination"]>a:last-child::attr(href)').extract_first()
        if next_text == '次の15件 >>':
            meta = {'review_url': next_url}
            yield scrapy.Request(url=next_url, meta=meta, callback=self.parse, dont_filter=True)
