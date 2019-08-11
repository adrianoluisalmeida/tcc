from scrapy.item import Item, Field

class YahooItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    code = Field()
    price = Field()