# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Curso(scrapy.Item):
    nombre = scrapy.Field()
    nrc = scrapy.Field()
    seccion = scrapy.Field()
    profesor = scrapy.Field()
    horarios = scrapy.Field()
    creditos = scrapy.Field()
