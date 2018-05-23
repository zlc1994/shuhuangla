import scrapy
import pymongo
from scrapy.loader import ItemLoader
from novelspider.items import Book


class BookSpider(scrapy.Spider):
    name = 'books'
    allowed_domains = ['yousuu.com']

    def start_requests(self):
        client = pymongo.MongoClient()
        db = client['items']
        book_lists = set([item['book_id'] for item in db['comments'].find()])

        for _id in book_lists:
            yield scrapy.Request('http://www.yousuu.com/book/{}'.format(_id), self.parse)

    def parse(self, response):
        l = ItemLoader(item=Book(), response=response)
        l.add_value('book_id', response.url.split('/')[-1])
        l.add_xpath('name', '//div[@style="height:30px;line-height:30px;"]/span/text()')
        l.add_xpath('tag', '//div[@id="booktag"]/a/text()')
        l.add_xpath('author', '//div[@class="media-body ys-bookmain"]/ul/li/a/text()')
        l.add_xpath('words', '//div[@class="media-body ys-bookmain"]/ul/li[2]/text()')
        l.add_xpath('chapters', '//div[@class="media-body ys-bookmain"]/ul/li[3]/text()')
        l.add_xpath('source', '//div[@class="media-body ys-bookmain"]/ul/li[4]/text()')
        l.add_xpath('last_update', '//div[@class="media-body ys-bookmain"]/ul/li[5]/text()')
        l.add_xpath('last_chapter', '//div[@class="media-body ys-bookmain"]/ul/li[6]/text()')
        l.add_xpath('info', '//div[@id="bookinfo"]/div/text()')
        l.add_xpath('pc_url', '//div[@class="media"]/a/@href')
        l.add_xpath('m_url', '//div[@class="media"]/a/@href')
        l.add_xpath('cover', '//img[@class="bookavatar"]/@src')
        return l.load_item()