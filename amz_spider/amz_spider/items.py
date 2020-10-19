# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AmzSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class AmzReviewItem(scrapy.Item):
    reviewId = scrapy.Field()
    asin = scrapy.Field()
    parentasin = scrapy.Field()
    rating = scrapy.Field()
    reviewer = scrapy.Field()
    reviewer_profile = scrapy.Field()
    review_time = scrapy.Field()
    msg = scrapy.Field()
    verified = scrapy.Field()
    helpful = scrapy.Field()
    comment = scrapy.Field()
    review_title = scrapy.Field()
    pageNo = scrapy.Field()
    countryCode = scrapy.Field()
    source_asin = scrapy.Field()

