# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ReviewsItem(scrapy.Item):
    product_url = scrapy.Field()
    review_url = scrapy.Field()
    review_time = scrapy.Field()
    review_raiting = scrapy.Field()
    review_title = scrapy.Field()
    review_body = scrapy.Field()
    critic_url = scrapy.Field()


class CriticsItem(scrapy.Item):
    id = scrapy.Field()
    critic_id = scrapy.Field()
    critic_url = scrapy.Field()
    age = scrapy.Field()
    sex = scrapy.Field()
    product_review = scrapy.Field()
    store_reviews = scrapy.Field()
    product_bad_review = scrapy.Field()


class ShopReviewsItem(scrapy.Item):
    review_type = scrapy.Field()
    product_name = scrapy.Field()
    product_id = scrapy.Field()
    review_detail_url = scrapy.Field()
    review_raiting = scrapy.Field()
    review_time = scrapy.Field()
    review_title = scrapy.Field()
    review_body = scrapy.Field()
