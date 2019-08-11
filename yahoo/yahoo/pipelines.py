import pymongo

class YahooPipeline(object):
    def __init__(self):
        self.conn = pymongo.MongoClient(
            'localhost',
            27017
        )
        db = self.conn['yahoo']
        self.collection = db['stock']

    def process_item(self, item, spider):
        self.collection.insert(dict(item))
        return item