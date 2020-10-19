
# 未使用
import random

agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
]
#es
header_Item = {
            "accept":"text/html,*/*",
            "accept-encoding":"gzip, deflate, br",
            "accept-language":"zh-CN,zh;q=0.9",
            "content-type":"application/x-www-form-urlencoded;charset=UTF-8",
            "origin":"https://www.amazon.fr",
            "user-agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
            "x-requested-with":"XMLHttpRequest"
        }

def get_random_header():
    headers = header_Item
    headers['user-agent'] = random.choice(agents)
    return headers