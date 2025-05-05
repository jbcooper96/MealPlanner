# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class RecipeItem(scrapy.Item):
    title = scrapy.Field()
    ingredients = scrapy.Field()
    instructions = scrapy.Field()
    tags = scrapy.Field()
    nutritionFacts = scrapy.Field()
