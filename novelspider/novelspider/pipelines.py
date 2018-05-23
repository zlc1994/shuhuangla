import pymongo


class MongoPipeline(object):

    comments_collection_name = 'comments'
    books_collection_name = 'books'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if 'rate' in dict(item):
            self.db[self.comments_collection_name].insert_one(dict(item))
        else:
            self.db[self.books_collection_name].update_one({'book_id': item['book_id']},
                                                           {'$set': dict(item)}, upsert=True)
        return item