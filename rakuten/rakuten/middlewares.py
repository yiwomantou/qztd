# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


class RakutenSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class RakutenDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class HeaderMiddleware:
    def process_request(self, request, spider):
        accept = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,' \
                 'application/signed-exchange;v=b3;q=0.9'
        cookies = '_ra=1600918367623|eac37563-ae8d-460c-a3c7-f927bf3d7252; Rp=1f62e5aaf14f01ad26811ba2d5f6c135f891d' \
                  'd; Rt=2c5a21f102e6ecf40a1ed93a29944e67; _fbp=fb.2.1600918393864.1702195549; _ts_yjad=16009183940' \
                  '99; __pp_uid=9CditbFfDPGQPhAqmTroYkHV200fqmhM; ak_bmsc=50FFEC9AEB1A80A8BCE9DF81536E569E1735219C7' \
                  '01D0000D245715FF3DC7F40~plvEMAbCLClowxguQTLsMul+tB2OROq90R1J3hIGs37VKrnUn8EtmAOfK2T2hujk8d4L1V90' \
                  '+mbfFh6smvZ4EotLdxlCa1IhR9JjyIKJCs8T/YeAgC0US60VS1TMMydiO1oD7IshWWCt/OiRORTLm6okwUqB3Z7i4GPjM1AY' \
                  'Yl9073AQFtoj9TfDxpyGZAGq5wotbU5aTRG7gkkCEgbXLHoYO+fsLNmNQr6xts61zKj+LFpDEHuRKykuvJTymjDaYv; Re=1' \
                  '3.10.0.0.0.565247.10-13.10.0.0.0.565247.10; rat_v=10c899ce20778811707045df2a5f715df82b7b8; s_per' \
                  's=%20s_mrcr%3D1100400000000000%257C4000000000000%257C4000000000000%257C4000000000000%7C175894521' \
                  '9414%3B; __gads=ID=7a0c27df6a95fec4:T=1601265221:S=ALNI_MatIds-3YG3HsiAlJHols5fS0fIHw; bm_sv=8E2' \
                  'BF8293DF0B930DC1533EA5A18FEF6~cqfWm3fin1gdnBpAH5XiusURn03x6tOJ+HNFgRMux4pOtqoXeeVxgCEHQO06fpj90j' \
                  'eKJONbzmP/Qt8q3ufdoUIVitHXDtMaTMn6AbkZwIe0hXxeoPT334DseaTJRhODT0MtFmq63DG/zKhwJ01TbQAefi1UjNMlEU' \
                  'jqAYpycmM='
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.' \
                     '4183.102 Safari/537.36'
        request.headers.setdefault('Accept', accept)
        request.headers.setdefault('Accept-Encoding', 'gzip, deflate, br')
        request.headers.setdefault('Accept-Language', 'zh-CN,zh;q=0.9,en;q=0.8')
        request.headers.setdefault('Cache-Control', 'max-age=0')
        request.headers.setdefault('Cookie', cookies)
        request.headers.setdefault('referer', 'https://item.rakuten.co.jp/')
        request.headers.setdefault('sec-fetch-dest', 'document')
        request.headers.setdefault('sec-fetch-mode', 'navigate')
        request.headers.setdefault('sec-fetch-site', 'same-site')
        request.headers.setdefault('sec-fetch-user', '?1')
        request.headers.setdefault('upgrade-insecure-requests', '1')
        request.headers.setdefault('User-Agent', user_agent)
        return None
