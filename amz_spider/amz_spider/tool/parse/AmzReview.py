# -*- coding: utf-8 -*-
'''
--------------------------------------------------------------
NAME:ReviewItem
作用:提取目标评论的详细信息，包括详情、发布日期等，针对发布日期已对多个不同站点进行适配
# 未使用
--------------------------------------------------------------
'''
from amz_spider.items import AmzReviewItem
import time
import urllib
import re


us_month =["January", "February", "March", "April", "May","June","July","August","September","October","November","December"]
def createReviewItem(div,parentasin,pageNo,countrycode):
    reviewId = div.xpath('@id')[0].strip("customer_review-")
    try:
        rate = div.xpath('div/a[@class="a-link-normal"]/@title')
        if len(rate) > 0:
            rating = 0
            rateArr = rate[0].split(' ')
            for r in rateArr:
                try:
                    r = r.replace(",",'.')
                    r = float(r)
                    if rating == 0 or rating > r:
                        rating = r
                except:
                    pass
        else:
            rating = 0
    except:
        rating = 0
    try:
        review_title = div.xpath('div/a[@data-hook="review-title"]/text()')[0]
    except:
        review_title = ''
    try:
        reviewer = div.xpath('div/span[@data-hook="review-author"]/a/text()')[0]
    except:
        reviewer = ''
    try:
        reviewer_profile = div.xpath('div/span[@data-hook="review-author"]/a/@href')[0].strip("/gp/pdp/profile/").strip("/ref=cm_cr_arp_d_pdp?ie=UTF8")
    except:
        reviewer_profile = ''
    review_time = div.xpath('span[@data-hook="review-date"]/text()')
    if len(review_time) > 0:
        review_time = review_time[0]
    else:
        review_time = ''
    if review_time != '':
        if countrycode  == 'us' or countrycode  == 'ca':
            review_time = review_time.strip('on ')
            review_time = time.strftime("%Y-%m-%d",time.strptime(review_time,"%B %d, %Y"))
        elif countrycode == 'fr':
            fr_month = ["janvier", "février", "mars", "avril", "mai","juin","juillet","août","septembre","octobre","novembre","décembre"]
            review_time = review_time.strip('le ').decode('utf-8').encode("latin-1")
            for each in range(12):
                if fr_month[each] in review_time :
                    review_time = review_time.replace(fr_month[each],us_month[each])
                    break
            review_time = time.strftime("%Y-%m-%d",time.strptime(review_time,"%d %B %Y"))
        elif countrycode == 'de':
            de_month = ["Januar","Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
            review_time = review_time.strip('am ').decode('utf-8').encode("latin-1")
            for each in range(12):
                if de_month[each] in review_time :
                    review_time = review_time.replace(de_month[each],us_month[each])
                    break
            review_time = time.strftime("%Y-%m-%d",time.strptime(review_time,"%d. %B %Y"))
        elif countrycode == 'es':
            es_month = ["enero","febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
            review_time = review_time.strip('el ').replace('de ','').decode('utf-8').encode("latin-1")
            for each in range(12):
                if es_month[each] in review_time :
                    review_time = review_time.replace(es_month[each],us_month[each])
                    break
            review_time = time.strftime("%Y-%m-%d",time.strptime(review_time,"%d %B %Y"))
        elif countrycode == 'it':
            it_month = ["gennaio","febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]
            review_time = review_time.strip('il ').decode('utf-8').encode("latin-1")
            for each in range(12):
                if it_month[each] in review_time :
                    review_time = review_time.replace(it_month[each],us_month[each])
                    break
            review_time = time.strftime("%Y-%m-%d",time.strptime(review_time,"%d %B %Y"))
        elif countrycode == 'jp':
            review_time = '-'.join(re.findall('\d+',review_time))
            review_time = time.strftime("%Y-%m-%d",time.strptime(review_time,"%Y-%m-%d"))
        elif countrycode == 'uk' or countrycode == 'au':
            review_time = review_time.strip('on ')
            review_time = time.strftime("%Y-%m-%d",time.strptime(review_time,"%d %B %Y"))
    asin = parentasin
    asin_url = div.xpath('div/a[@data-hook="format-strip"]/@href')
    if len(asin_url) > 0:
        asin_url = asin_url[0]
        asin_url =  urllib.unquote(asin_url).decode('utf-8', 'replace').encode('gbk', 'replace')
        asin = asin_url.split('product-reviews/')[1].split('/')[0]
    try:
        verfiled = div.xpath('div/span[@data-action="reviews:filter-action:push-state"]/@class')[0]
        verfiled = 1
    except:
        verfiled = 0
    try:
        msg = div.xpath('div/span[@data-hook="review-body"]/text()')[0]
    except:
        msg = ''
    try:
        comment = div.xpath('div/div/a/span/span[@class="review-comment-total aok-hidden"]/text()')[0]
    except:
        comment = 0
    try:
        helpful = div.xpath('div/span[@data-hook="review-voting-widget"]/span/span/span[@data-hook="helpful-vote-statement"]/text()')[0].strip('n ').strip()
        if helpful[:30] == 'One person found this helpful.':
            helpful = 1
        else:
             helpful = helpful.strip(' people found this helpful.')
    except:
        helpful = 0
    
    item = AmzReviewItem()
    item['reviewId'] = reviewId
    item['asin'] = asin
    item['parentasin'] = parentasin
    item['rating'] = rating
    item['reviewer'] = reviewer
    item['reviewer_profile'] = reviewer_profile
    item['review_time'] = review_time
    item['msg'] = msg
    item['verified'] = verfiled
    item['helpful'] = helpful
    item['comment'] = comment
    item['review_title'] = review_title
    item['pageNo'] = pageNo
    item['countryCode'] = countrycode
    return item

def getUrlParameter(url):
    param = {}
    url =  urllib.unquote(url).decode('utf-8', 'replace').encode('gbk', 'replace')
    param['asin'] = url.strip('https://www.amazon.com/product-reviews/').split('/')[0]
    arr = url.split('&')
    arr_len = len(arr)
    for i in range(arr_len):
        if i == 0:
            continue
        keyarr = arr[i].split('=')
        if len(keyarr) > 1:
            param[keyarr[0]] = keyarr[1]
    return param
