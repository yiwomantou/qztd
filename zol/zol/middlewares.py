# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import requests
from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


class ZolSpiderMiddleware:
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


class ZolDownloaderMiddleware:
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


class ProxyMiddleware:
    def process_request(self, request, spider):
        proxy = self.get_proxy()
        print('获取代理{}'.format(proxy))
        request.meta['proxy'] = 'http://' + proxy
        return None

    def get_proxy(self):
        proxy = requests.get('http://localhost:5555/random').text
        return proxy


class HeaderMiddleware:
    def process_request(self, request, spider):
        accept = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,' \
                 'application/signed-exchange;v=b3;q=0.9'
        cookies = 'ip_ck=7sCH5/Lyj7QuOTc2MDg1LjE1OTkwMTM5OTE%3D; realLocationId=9; userFidLocationId=9; listSubcate' \
                  'Id=16; Hm_lvt_ae5edc2bc4fc71370807f6187f0a2dd0=1599013993,1600422680,1600477744,1600477756; BAID' \
                  'U_SSP_lcr=https://www.baidu.com/link?url=IHoYik4rEcQu2m_lbcIPKr8UQtap9N3hFGOScc4VgGO&wd=&eqid=f7' \
                  '8792b600047ab3000000065f655a38; Adshow=1; lv=1600648926; vn=5; z_pro_city=s_provice%3Dguangdong%' \
                  '26s_city%3Dshenzhen; userProvinceId=30; userCityId=348; userCountyId=0; userLocationId=9; Hm_lpv' \
                  't_ae5edc2bc4fc71370807f6187f0a2dd0=1600654844; z_day=ixgo20=1&izol110792=6&rdetail=7; questionna' \
                  'ire_pv=1600646407'
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.' \
                     '4183.102 Safari/537.36'
        request.headers.setdefault('Accept', accept)
        request.headers.setdefault('Accept-Encoding', 'gzip, deflate')
        request.headers.setdefault('Accept-Language', 'zh-CN,zh;q=0.9,en;q=0.8')
        request.headers.setdefault('Cache-Control', 'max-age=0')
        request.headers.setdefault('Connection', 'keep-alive')
        request.headers.setdefault('Cookie', cookies)
        request.headers.setdefault('Host', 'detail.zol.com.cn')
        request.headers.setdefault('Upgrade-Insecure-Requests', '1')
        request.headers.setdefault('User-Agent', user_agent)
        return None
