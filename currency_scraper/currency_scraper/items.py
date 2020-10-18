# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Currency(scrapy.Item):
    name = scrapy.Field()
    brazilian_real = scrapy.Field()
    american_dollar = scrapy.Field()
    european_euro = scrapy.Field()
    british_pound = scrapy.Field()
    japanese_yen = scrapy.Field()
    swiss_frank = scrapy.Field()
    canadian_dollar = scrapy.Field()
    australian_dollar = scrapy.Field()
    date = scrapy.Field()
