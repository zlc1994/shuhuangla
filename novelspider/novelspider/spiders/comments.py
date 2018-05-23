import scrapy
import time
import re
import redis
from scrapy.loader import ItemLoader
from scrapy.exceptions import CloseSpider
from novelspider.items import Comment


class CommentSpider(scrapy.Spider):
    name = 'comments'
    allowed_domains = ['yousuu.com']
    r = redis.StrictRedis()

    crawled_flag = r.get('crawled_flag')

    def start_requests(self):
        yield scrapy.Request('http://www.yousuu.com/comments', self.parse)

    def parse(self, response):
        xpath = {
            'user_id': './/div[@class="media-body"]/h5/a/@href',
            'book_id': './/div[@class="ys-comments-message"]/small/a/@href',
            'rate': './/span[@class="num2star"]/text()'
        }

        for comment in response.xpath('//li[@class="media ys-comments-left"]'):
            try:
                l = ItemLoader(item=Comment(), selector=comment)
                user_id = comment.xpath(xpath['user_id']).extract()[0].split('/')[2]
                book_id = comment.xpath(xpath['book_id']).extract()[0].split('/')[-1]
                rate = comment.xpath(xpath['rate']).extract()[0]
                key = '{0}-{1}'.format(user_id, book_id)
                if self.crawled_flag and self.r.sismember('comments', key):
                    raise CloseSpider('comments already exist')
                self.r.sadd('comments', key)
                l.add_value('user_id', user_id)
                l.add_value('book_id', book_id)
                l.add_value('rate', int(rate))
                l.add_xpath('body', './/p/text()')
                comment_time = re.search('\d+', response.url)
                if comment_time:
                    l.add_value('timestamp', int(comment_time.group(0)))
                else:
                    l.add_value('timestamp', int(time.time()))
                yield l.load_item()
            except IndexError:
                pass

        next_page = None
        try:
            tag = response.xpath('//a[text()="点击加载下一页"]/@onclick').extract()[0]
            comment_time = re.search('\d+', tag).group(0)
            next_page = 'http://www.yousuu.com/comments?t={}'.format(comment_time)
        except Exception:
            pass

        if next_page:
            yield scrapy.Request(next_page, callback=self.parse)

    def close(self, reason):
        self.r.set('crawled_flag', 1)
