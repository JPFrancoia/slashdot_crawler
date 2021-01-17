# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo
from loguru import logger


class SlashdotCrawlerPipeline:

    collection_name = "articles"

    def __init__(self):
        self.mongo_uri = "mongodb://localhost:27017/"
        self.mongo_db = "slashdot_db"

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

        if self.collection_name not in self.db.list_collection_names():
            self.db[self.collection_name].create_index("title", unique=True)
            self.db[self.collection_name].create_index("url", unique=True)

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        try:
            self.db[self.collection_name].insert_one(ItemAdapter(item).asdict())
        except pymongo.errors.DuplicateKeyError:
            logger.debug(
                f"Item with url {item['url']} already in the DB"
            )
        return item
