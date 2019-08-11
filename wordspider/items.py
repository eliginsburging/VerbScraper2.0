# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class WordspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    example = scrapy.Field()
    translation = scrapy.Field()


class StressspiderItem(scrapy.Item):
    stressed = scrapy.Field()
    clean = scrapy.Field()
