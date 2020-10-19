import re
# 今天我主要是把服务器的环境搭建起来，测试可用
# 我对服务器运行爬虫的理解，我认为目前的体量没必要在服务器上跑，服务器上的代码是稳定版本，不需要改动的，但是目前的需求
# 不需要24小时连轴转，所以我任务我不需要服务器，以后可能需要
# 我现在把本职工作做完之后尽可能的去学习
# 我现在学习的所有数据分析都是操作而不是想法，我都是在学怎么做而不是为什么这么做
# s = 'Amazon Bestseller-Rang: Nr. 2,041 in Elektronik & Foto Nr. 56 in HDMI-Kabel Nr. 56 in HDMI-Kabel'
# s = 'Nr. 17,854 in Computer & ZubehörNr. 429 in Monitore'
# print(s.split('Nr. '))
# print(s.split('Nr. ')[1].split(' in ')[1].split(' (')[0])
# print(s.split('Nr. ')[-1].split(' in '))

# s = '#1,230 in Tools & Home Improvement (See Top 100 in Tools & Home Improvement)#22 in Safety Goggles & Glasses'
# print(s.split('#'))
# print(s.split('#')[1].split(' in ')[1].split(' (')[0])
# print(s.split('#')[-1].split(' in '))

# s = 'https://www.amazon.de/dp/B00B2HORKE'
# print(s.split('/')[-1])
# {'asin': 'B01G9J08Q6', 'bigCategoryName': 'Tools & Home Improvement', 'bigRank': 1401,
# 'smallCategoryName': 'Safety Goggles & Glasses', 'smallRank': 22, 'five': '81%', 'four': '11%',
# 'three': '4%', 'two': '1%', 'one': '2%', 'price': '14.97', 'min_price': 0, 'rating_star': '4.7 out of 5',
# 'rating_num': '1,880 ratings 1,880 ratings', 'content': ''}

# s = '1,880 ratings 1,880 ratings'.replace(',', '')
# print(re.findall(r"\d+\.?\d*|$", s))

# s = 'for "protective eyeglasses"'
# print(s.split('"')[1])

# s = '1 213'
# print(''.join(s.split()))

import requests

proxies = {
    "http": "120.78.212.251:28888",
}

res = requests.get("http://www.baidu.com", proxies=proxies)
print(res.text)
print(res.status_code)
