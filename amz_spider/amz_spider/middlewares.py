# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import os
import sys
import time
import hashlib
import requests
import urllib3
import logging
from scrapy import signals
from scrapy.http import HtmlResponse

logger = logging.getLogger(__name__)
from OpenSSL import SSL
from scrapy.core.downloader.contextfactory import ScrapyClientContextFactory


# available_proxy = ['83.97.23.90:18080', '191.232.179.185:8080', '14.140.131.82:3128', '103.195.4.211:3128',
#                  '13.209.155.88:8080']
# available_proxy = ['69.197.181.202:3128', '212.98.143.138:8082', '95.111.245.169:3128']


class AmzSpiderSpiderMiddleware(object):
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

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
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


class AmzSpiderDownloaderMiddleware(object):
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


# class ProxyMiddlproxy_servereware(object):
#     def process_request(self,request,spider):
#         request.meta.get('try_count', 0)
#         proxy_data = requests.get("http://127.0.0.1:5010/get/").json()
#         print('==================', proxy_data)
#         if request.url.startswith("http://"):
#             request.meta['proxy'] = "http://" + proxy_data['proxy']  # http代理
#         elif request.url.startswith("https://"):
#             request.meta['proxy'] = "https://" + proxy_data['proxy']  # https代理
#         self.update_fail_count(proxy_data['proxy'])
# request.meta['proxy'] = {'http': 'http://'+proxy_data['proxy'],
#                           'https': 'https://'+proxy_data['proxy']}

# return
# def process_response(self, response, spider):
#     if 'proxy' in response.status == 503:
#         proxy = response.meta['proxy']
#         self.update_fail_count(proxy)
# print("Change proxy")
# request.meta['proxy'] = 'http://' + self.get_proxy()
# return


class ProxyMiddleware(object):
    """代理中间件
    """

    def process_request(self, request, spider):
        """对request加代理设置

        Args:
            request (obj): 请求对象
            spider (obj): 爬虫对象
        """

        # 由于请求出错时无法对代理进行操作，所以每次取一个代理就将其从代理池中删除，若响应码为503则置后，200则至前，无响应则该代理删除
        if request.meta.get('middle_state', True) == True:
            # proxy = self.get_proxy()
            # print('==============', proxy)
            # request.meta['proxy'] = 'http://' + proxy
            # self.delete(proxy)
            cookie_dict = {
                "us": "session-id=145-5209209-9478023; i18n-prefs=USD; ubid-main=133-8276981-7688751; x-wl-uid=1PCOyx0JI1kz7vWchZyMhRWJtqj1XoQoE0UNJPLhOT/Q8+kepq170hFhtVj1OBOSit46HW9f+Rz8=; lc-main=en_US; session-id-time=2082787201l; session-token=3TtwIpr/LCK/R5dUusiKqRfu1FQJmG80o4BC0knm7brPg8aelaJ+f/B16GedWlTyDSjn8qQo3s3PmGmw5mHywT8RWHthFHuduD76fCQKbeUHR0G/OJ4sj2eZxXUoxgcWn+a+xbKm+Rpj5ciXMPsk4ObS1HmuF5NFMFttjbT4ZsWQBxh5Ak9x1hxbsqNIrrrW; csm-hit=tb:0YBA58R18R2BQ1H4SWX6+b-0YBA58R18R2BQ1H4SWX6|1592453272955&t:1592453272955&adb:adblk_yes",
                "de": 'x-amz-captcha-1=1600138143463452; x-amz-captcha-2=CqAHXdW7T0rlVbPqMkzSKQ==; session-id=257-2895000-7745305; ubid-acbde=262-1345253-6301901; session-token=RjUjkGGQUDXlBqjqFI/4pk3K5OqGMoln3gJHzmxF/vcFCX5Tkljl4xX0taKhiN1WDfU3vSBFcPg7wZgi1RZ1QU/gfQFpujOz+PzWnTKs+5hVd4YbLUqwVg/ih9XWaxBtqQMQErsZNDJS8uR1qpgd0jRsW9S/4VihOPF4kVaZ/gk73+DfuZtUZyNVMlRwFwosNXFfbrPWsR0rXYvvsAIs/VxbG5oPAg1d5Myno0NvCrOXpYWhNw1TNveciJflhj+nWf7kXEwC8gv6efXiKSiMWTNGT8PdWd/1; x-acbde="6N@kfA3YbvcEg0mGrEro@xdWQ3PczUguDbeZIyQ6Hym3bVK2dDVzug8TYZBpzESg"; at-acbde=Atza|IwEBIABeShqmSCc0ta95wranyqqXcY-2z-bIoqtSJn2kasFv4BH6hYqcHy2bTy6WCltUowTDAkPXdQUzIDkJDsqM1iAvrgM2S7ZrsGb4eDi8vESDa-PW54nKE7RHftxBhFFCFh-R15jzM8XcK8DHrFv_tNjCzjpTBmcfef6vQ74oJcyGnvfWQhuxj2A2Kvg4voCBtTaxfsiqRojUYDJlPlpfLhFA; sess-at-acbde="hzNHLGfd9i0Tl01ttEBqnx+UaSuoxDEGjexAIWDqdOY="; sst-acbde=Sst1|PQEtPasEFHRRk02vx32yiieMCR6lf-VNjaUlFpbhVdu4N1aK6foF7TbxawkhwyyqkiMEU7vu-vX3o_e_8GO3Z9eVkrHK783_vJkoBzWn5GFjGMBC8A7VHFH_OWEUNXHsepsjxHMH1DaPDbtFGZL0hxNop2tNfSw3Y9kg2X3LQawgMkmUs5CDMQ7n9fySZB_nSJutpCLn7cPfP935TjEqMq3a6-rbMPzRaxOSczYC3IFBPzSjtKkZ2bnkRPb7tXg5FtAiej1vOHqzJ0vaBYd4v8SFrsfyVqt0yIOtzF5VPsEMKHM; lc-acbde=de_DE; csm-hit=tb:s-TNJT41JXH39H41QB9799|1602496821129&t:1602496821334&adb:adblk_no; i18n-prefs=EUR; session-id-time=2082754801l',
                "uk": 'session-id=261-9591895-0231046; ubid-acbuk=259-6383929-0758408; session-token=vUe7DLDJTgnTUZTWh3ek2xC9UU5ZubYbJV/6ZC+G1cz8seVQvqe/akX9/8w3LPIJhBanxrOkD/AT5pKNAkGN    LqdoTf1M4vcu4AR1fx5Pl9hnKgIIylXao0vBaFhEA1oq7DMhCjzHt34b8jSSFw4PT9fOLuZbFmoTFvvznVM+kQUaL0Ozlsx2D9ulKiaSYgKlMOFXmHcniewe2xkHg/Ey1nfqNvydc8LN8FM8X4aL5maqVhV3OSFZZ9aXS5AvWWW7XNBfyLgtBaYyg    MgN2IHnqmk6ZGNXUkTp; x-acbuk="ZX0JL0O19487aEKX7Ie7p5hv3daJJR2xQg7fmQMQ5zK7WGu@tA6sWXoDRzDiigba"; at-acbuk=Atza|IwEBIC3T2ri3c55q_HZsJO2xgTy8B3zE-6BHRY1CnZ9jxY_eWthUi6VHnQ9j-0MIgokBVBM2TF    h4_MUm8VgpjaewBmZYfKRtKI6d8a13k2V5styhYq1qCTOgnNmCGn5jz6w3jWzRVAsFDCBmUfPsjYNyt6VlRyh5v2GTrBy-oBjws7rHljK5W76YrxknI7nvlfybOnbr_ztBdm_Ifn8G2FMAtARt; sess-at-acbuk="hDaJDGD6AJtq4ysH+OApxa    0xOj4ggGhhfPyHtx+1KeI="; sst-acbuk=Sst1|PQGz64V6Jv2sOM8TPCdHKLUVCWPxH5Y7ax9kRWCSCxpnsfxI2oF6zEkq_oruvyVcv2i7bwUfXFVxoKxVzgViWQoojukUcu3IVQ4ASrLJo6ilstsf-w6QU_qA3g_aSR6J1c_NVCZMTj0FAAife    Xu2f7RjR8jPy4ZZt5uY_S6_rhNtByl0lQ5l7nqOZbjNRIqWvBcX9VOxMYCiEg8XC2E0SUfrw0HcHgV2b8KQB7LwJcUbgcayhoblKeFpPn2VgKgI171NnZoTOzCkEI2w4DTzfS_Cs2jPc0OV0-JB4aZ4vbOp4iI; lc-acbuk=en_GB; i18n-pref    s=GBP; session-id-time=2082758401l; csm-hit=adb:adblk_no&t:1599621461170&tb:J8NYBA9VE00MXX47A6QA+s-Y44RHH30WZ0MRZF2S6N9|1599621461170',
                "fr": 'x-amz-captcha-1=1600149924411258; x-amz-captcha-2=m4yXjfS/U2I0brI7vnehPA==; lc-acbfr=fr_FR; session-id=259-6239319-9144904; ubid-acbfr=259-7658976-0556418; x-acbfr="n0DuqUTu@MEmF@DLo91un@C0dDJdU97CTutMY7GSBFDb9l6P1gks@KNncvHlY2dr"; at-acbfr=Atza|IwEBILxh1YjfkyMk-IgyfeO2bSs-6NjTeA_1oOUkAaJeyOj7aEuzMZinFUKaIQ3pAN7UsSmMmr06tIRvkIj-qDT0Yw6XbV3QsZ_bDGiWRdo5GeOxPGQxn_U-74RaPo3B3PM51gW8OXUcSpFNqK6YLV1sTuNco5epeoSGBFJesb2gn0S3LdcU4mjYLvzEV3B-PRb-O3Gs1vfttH11K94HiaibhaXOGU9DHUSLkyeskju8k9cYQw; sess-at-acbfr="ekZBC8CNQlwpZIhf7gQFH5u5BlATP269Eb3RLo0k5VA="; sst-acbfr=Sst1|PQG8qwgmdK0TW0r3C5dpu24ECQv0b6TgH8GDcecNGmOAcTM1RBFHEVvwLolzAbRgfnrnzE4jRZDC6COP2XYI3KY0-Z6cicwzCbcmZhMgWHqW_Zk55QeG4dzsr_WI0SSOyIazucXJ1HMnbIEJXyCSbDV-t8Y2OhRqNJ499df30RMDYSjAmTYJQ19lSju0bBTzeSuiyoFxVJe0xgnSE_igmfH6PWTjhqEkxGt12DCvLYQUY6eqMagyq_54Q09EcAU90heIMs1-RioDPfY__zP_O7KV6TyTfcdFCVH8RCL72sfCuxI; i18n-prefs=EUR; session-id-time=2082787201l; session-token="76EvYHECTUKLyXOCFACXvg9Z2ZGB+ihl6/BHW888BXw8AHxhMQ/JgulhqEBQAyHYpyNB5efzEiWW2kepDIcxfeAx0JMq6M9O+GfYZ63VVtVFZiOYzbdDe8hjyZTfMZCm/AacfnNRBnDcnCIn2IB4DAB8TsOKvP5dJF+aaGaA60YJW6dbj4zNqG9lds9aHDwbdmWrogOE6zGqN6v4hQhoOQ=="; csm-hit=tb:s-SGGFVT8GEN58EXATWSS3|1602639168216&t:1602639169107&adb:adblk_no',
                "it": 'x-amz-captcha-1=1599817306445948; x-amz-captcha-2=v2rEG314PhcV2LhqZpUaHA==; at-acbit=Atza|IwEBIPcNa1n1e2OzEmbvBP9_jpK5xE0imuG6cnFOo_Zl2WfgCcjW89LXFgF2-HvdtRt6YLnDwgNjbjFyr4DEHwvwlcXha2J7txz_at96-MjizqmPYoD-T3TXwmJP02Sp8B6iJX0wUFYM_BNqrs5oXuq_8BV72pPa0H__pE5_9t-BWGEOCdj7TGTLpINxyW-_gmlpFQM7vFldZ0GkshLqXeH8WvZ_cBbtD4rF0YcJB3un_Zgdgw; sess-at-acbit="hGGWCgsPaB1ShEc8Po4hkV9LABIaZv4LLDKzhAiELTQ="; sst-acbit=Sst1|PQEdfLiB1jVQY1zvmX8kSRjuCXYqcGGNrUSqFECiXj4cxbWt1ARRpuoSuOkrHDE5fTVJdGTWt7_4qOJJtFKLQHxbSmqxgzBEleGsjAzld4vWJBABZxLEIAADOwLYFGCbNulH8Mgj5qTcrzZbJiF95O4Do34DYng0w10WCDaFyw3GRs4zDL-f0rnQAO2b9s7dCViDuRplGz4wrqJZbwG9UQ6OOYgnLK9p0aKefseWAqsXWRpPO3feMxYnXKfkpGmmolp1NnWxuo5Dnj2kEVbsJ-IFYwzIcEon6ou-SR122gF8SBg; x-acbit=vvfrYcGMVtCOV8ssj7bbVAAB9D5sLGfEv30TZ7UOIV2JSF7dZTEWTkgngbWJd1qX; i18n-prefs=EUR; lc-acbit=it_IT; session-token="bHL7IYpYP6yEQ2XAHBn4eyaXW9PU9/6ydzPWGozYkrJ07dJQvLrQomsMXZYO5yP2m2ByOFhXZSSfjRFmcy0kZg/MyxUJtab1AM8FwIgVOmX4JGPA1BvEwXmp+pE4q+e3wAXDQI0n7u/SH+f7oyDr5u85lL9jXRKCGSFClGEW1U0JDaKvLJkpgalZvr79m62/uDGGVxjcj//5UD9yZTilT7F7ao1BQ6qJM8eAHMkHuiwQeRYTSOezK4AzappbaUEuzd+Te4VLD4JQojU+wHS0yg=="; csm-hit=tb:s-YVMN3341F8QGR29ZQF3A|1600051324699&t:1600051334374&adb:adblk_no; ubid-acbit=262-6383973-7915307; session-id-time=2082758401l; session-id=261-5766352-7099144',
                "jp": 'session-id=357-0727037-9760655; ubid-acbjp=355-4201959-7943311; lc-acbjp=en_US; session-token="QI4ppDkr+/OlJTfHUpGccJ06/RgwCQDFX7VTgZeS+le5GBwFLddYuv1wz3FWMrhk6796mmEz2HMIOQTAkLHCkWTt16zw5K2I2xi6gA8AX06twT+VcZhHQbbtA/995YT03N2gKtGOm0zTnbZHvb1go8YGpRVOmGk7JR2BGB0vyR6LMd0lbNrPtOhMOV5hvHh6Aw8iPCG1Inlv+Imm8kSQAWexeC+SHZBizcfF/i+IOT9epUjq4lAXUt3mnOB3+qZ92Y/gtVEDSknWVYkyqX48ug=="; x-acbjp="dHb@pufYAfod?7lc?SbpE7oT4QueJkgx8TeIJarJG1EK415aKKuCWIXTLZR5fSg3"; at-acbjp=Atza|IwEBIFfgPiTs6cG6kvAMLqJGfbKhnnopccdfl_1muHQApX_KDv8qimXTwqvfWgTubbX31fffdOUvDXJw2s7ENAAgedCxkvURrDTnuCsoAU0FEAzOa88HhE6WDENR2OAzb6nb6jxnZFQkd34wx_TWd2ubDswd6S-V73oOIl41KndjOu-nWsPOZNuXadokyl9Kv3uc4iW21DThkOGr9ANcigcy1aU3; sess-at-acbjp="vy6+dPSIohcinZqdKlkX4v0qigaV1crvSkpMhYYfNKk="; sst-acbjp=Sst1|PQFj972QpQs02RGxSZdrSOFNCay0G4QHcJ_UpaE3DZeJwy9k1GKXLsM3jX6DP089GMbnZnO-Lp-rQ_Q4PSKrvgXjWrfJfAV2XXIvmMVSNzVTs-XM7qqIzkebM-niKmZV8R3bnA7v-AfDDO4FvZ3eBj7fD_dUBfnMqPcknz0FGH-_WyzpY3gIx585Z1oX4Cw0r3gomVyqJA6asSRVXNX9zS5GCJomOKvQnLZd1TuxeDUysjg432vAN1PzNq13L9VkK2KGFAMGnfmKpFnPZMmDJSpvDewS3NE0Q5YwijSNHrfHfJs; i18n-prefs=JPY; csm-hit=tb:s-2QW76WDJP4WBHCZ6XM0Q|1599792350324&t:1599792350455&adb:adblk_no; session-id-time=2082726001l',
                "es": 'x-amz-captcha-1=1599817529705760; x-amz-captcha-2=gO/WhkQ/tUh+TRqKQVkgtA==; at-acbes=Atza|IwEBIGPHGJqOXz9arCg8YdSjTlx81dXoTD-lK3a7Gh7bbHmXjPCv9w0a7KkwQ38db8PhDJMTvDL0NTd_VPv_T-NGivzs5pXWTs15zCBr8UStgi19JiizcAxZO3pBjEp1l4E9f9EiLn6NnMlDe4uAjotf_6LIbhI-QcDTBz5t8bjjc_cBSrLcCTUwJOM2QDTmGKyzQijS2e3iKyR6qLcwcY1Yj3HPjOzUQQ4TAR6GwJfUpXbR3Q; sess-at-acbes="1QaSKi4iVkU3wY7kk0A2lcHdIF3z2koYH8QxRXKttzA="; sst-acbes=Sst1|PQH_FQlsn0YXrWqsH8Tn5629CW1FC1yye4wCkNp4S8wgP3jcaFe-oRAUMlDd080nlGaXHaMblP3heg3Cd-Me77ndjLnTdIK7qaWT3PBOED9Es0RGtGi3t-qQVf6QIY9f21Koe8-4vTT6iZOB2H0Xwa4teymwgGN1bpBVBnWXbzsu3txF_OexOBqkk5Kp_dr7v5HW9OypUgAiNfdV6Rba1c7ag-x3yL0i-urb9ljkd_X-DbgYeqZ9bposrqLtc1YCuvDnC5M5WsXBr2abQJ6I25fS7y-yFFk-Qzu9XufGNx9mjlo; csm-hit=tb:s-WPZD6DXGPMD8M01N2H54|1600051562021&t:1600051562642&adb:adblk_no; session-token="8dH4APwRpFadapIMBJeArmZ/SHGt7pY28rNOEYp1zpJIouGiYEmi5hA4CT35PzPIyP9ajzOW68a8p3hhYYxINkDgppjDd94ViOJkQuvgnZuRcRl2Cxp1ehCkFK+VsTOLKDfvjKZAFoJOidJ5s30MRATy1+qftp5Lclgg3Xz9hKOp+8zY5be2HingJYcLek9UPEGK0THXlFKc8CKsMAvohxV0LBpqc6xHTTUxkls2wbuzD33psacHP3mNg9sqr4XLRWGye55gEP4ujko4C/0u8w=="; x-acbes="@6RGXz762GjbVvzXIopDGbBrjonamXOutgjeOhSlSaYUWZe1@0OE4b5?zOpsR0Wz"; i18n-prefs=EUR; lc-acbes=es_ES; ubid-acbes=262-8498064-6882357; session-id-time=2082758401l; session-id=259-6441571-0395934',
            }
            request.headers.setdefault('Cookie', cookie_dict[request.meta.get('country', 'us')])
            request.headers.setdefault('Accept', 'application/json, text/plain, */*')
            request.headers.setdefault('Accept-Encoding', 'gzip, deflate, br')
            request.headers.setdefault('Accept-Language', 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7')
            request.headers.setdefault('Cache-Control', 'no-cache')
            request.headers.setdefault('Connection', 'keep-alive')
            request.headers.setdefault('Pragma', 'no-cache')
            request.headers.setdefault('Sec-Fetch-Mode', 'cors')
            request.headers.setdefault('Sec-Fetch-Site', 'same-origin')
            request.headers.setdefault('User-Agent',
                                       'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36')


        else:
            pass

    def get_proxy(self):
        """获取代理

        Returns:
            str: 代理
        """
        while True:
            try:
                # proxy = requests.get('http://127.0.0.1:5010/get/').json()['proxy']
                # proxy = requests.get('http://localhost:5555/random').text
                # proxy = random.choices(available_proxy)[0]
                proxy = '120.78.212.251:28888'
                break
            except:
                # 备用代理池，当本机代理池代理被用完时从备用代理池取代理
                # proxy = requests.get('http://127.0.0.1:5010/get/').json()['proxy']
                # proxy = requests.get('http://localhost:5555/random').text
                # proxy = random.choices(available_proxy)[0]
                proxy = '120.78.212.251:28888'
                break
        return proxy

    def update_check_count(self, proxy):
        """更新代理的校验次数

        Args:
            proxy (str): 代理
        """
        params = {
            'proxy': proxy
        }
        # requests.get('http://127.0.0.1:5010/update_check_count/', params=params)

    def update_fail_count(self, proxy):
        """更新代理的失败次数

        Args:
            proxy (str): 代理
        """
        params = {
            'proxy': proxy
        }
        # requests.get('http://127.0.0.1:5010/update_fail_count/', params=params)

    def process_exception(self, request, exception, spider):
        """当代理异常时，更换代理

        Args:
            request (obj): 请求对象
            exception (obj): 异常
            spider (obj): 爬虫对象
        """
        if 'proxy' in request.meta:
            proxy = request.meta['proxy']
            self.update_fail_count(proxy)
            print("Change proxy")
            request.meta['proxy'] = 'http://' + self.get_proxy()

    def delete(self, proxy):
        """更新代理的失败次数

        Args:
            proxy (str): 代理
        """
        params = {
            'proxy': proxy
        }
        # requests.get('http://127.0.0.1:5010/delete', params=params)


class DynamicForwardMiddleware(object):
    def process_request(self, request, spider):
        data = self.dynamic_forward(request.url)
        return HtmlResponse(url=request.url, body=data.get('body'), request=request, encoding='utf-8',
                            status=data.get('status'))

    def dynamic_forward(self, url):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        _version = sys.version_info

        is_python3 = (_version[0] == 3)

        env_dist = os.environ
        orderno = env_dist.get('dynamicforward_orderno')  # 填写讯代理的订单号
        secret = env_dist.get('dynamicforward_secret')  # 填写讯代理的secret

        ip = "forward.xdaili.cn"
        port = "80"

        ip_port = ip + ":" + port

        timestamp = str(int(time.time()))
        string = ""
        string = "orderno=" + orderno + "," + "secret=" + secret + "," + "timestamp=" + timestamp

        if is_python3:
            string = string.encode()

        md5_string = hashlib.md5(string).hexdigest()
        sign = md5_string.upper()
        # print(sign)
        auth = "sign=" + sign + "&" + "orderno=" + orderno + "&" + "timestamp=" + timestamp

        # print(auth)
        proxy = {"http": "http://" + ip_port, "https": "https://" + ip_port}
        headers = {"Proxy-Authorization": auth,
                   "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36"}
        r = requests.get(url, headers=headers, proxies=proxy, verify=False, allow_redirects=False)
        r.encoding = 'utf8'
        if r.status_code == 302 or r.status_code == 301:
            loc = r.headers['Location']
            r = requests.get(loc, headers=headers, proxies=proxy, verify=False, allow_redirects=False)
            r.encoding = 'utf8'
        return {'body': r.text, 'status': r.status_code}


if __name__ == '__main__':
    p = ProxyMiddleware()
    print(p.delete('35.220.130.255:5357'))
