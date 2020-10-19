# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SeriesItem(scrapy.Item):
    brand_name = scrapy.Field()
    brand_url = scrapy.Field()
    series_name = scrapy.Field()
    series_url = scrapy.Field()


class ModelItem(scrapy.Item):
    product_name = scrapy.Field()
    product_url = scrapy.Field()
    product_data_interface = scrapy.Field()
    product_video_interface = scrapy.Field()
    product_audio_interface = scrapy.Field()
    product_other_interface = scrapy.Field()
    product_card_reader = scrapy.Field()
    product_series_url = scrapy.Field()
    conf_url = scrapy.Field()
