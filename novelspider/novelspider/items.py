import scrapy
from scrapy.loader.processors import TakeFirst, Compose, MapCompose


def filter_word(string):
    try:
        return string.split(':')[-1]
    except IndexError:
        return None


class Comment(scrapy.Item):
    user_id = scrapy.Field(output_processor=TakeFirst())
    book_id = scrapy.Field(output_processor=TakeFirst())
    rate = scrapy.Field(output_processor=TakeFirst())
    body = scrapy.Field(output_processor=TakeFirst())
    timestamp = scrapy.Field(output_processor=TakeFirst())


class Book(scrapy.Item):
    book_id = scrapy.Field(output_processor=TakeFirst())
    name = scrapy.Field(output_processor=TakeFirst())
    tag = scrapy.Field(output_processor=TakeFirst())
    author = scrapy.Field(output_processor=TakeFirst())
    words = scrapy.Field(output_processor=Compose(lambda x: x[0], filter_word))
    chapters = scrapy.Field(output_processor=Compose(lambda x: x[0], filter_word))
    pc_url = scrapy.Field(output_processor=TakeFirst())
    m_url = scrapy.Field(output_processor=Compose(lambda x: x[-1]))
    info = scrapy.Field(output_processor=TakeFirst())
    source = scrapy.Field(output_processor=Compose(lambda x: x[0], filter_word))
    last_chapter = scrapy.Field(output_processor=Compose(lambda x: x[0], filter_word))
    last_update = scrapy.Field(output_processor=Compose(lambda x: x[0], filter_word))
    cover = scrapy.Field(output_processor=TakeFirst())