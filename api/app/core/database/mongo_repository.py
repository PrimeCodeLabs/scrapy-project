import pymongo

class MongoRepository:
    def __init__(self, uri, db_name, collection_name):
        self.client = pymongo.MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        self.collection_name = collection_name

    def save_data(self, data):
        if isinstance(data, list):
            self.collection.insert_many(data)
        else:
            self.collection.insert_one(data)
    
    def get_data(self, query={}, projection=None):
        return list(self.collection.find(query, projection))
    
    def get_all_data(self):
        return list(self.collection.find())

class MongoStrategyRepository:
    def __init__(self, uri, db_name):
        self.client = pymongo.MongoClient(uri)
        self.db = self.client[db_name]

    def insert_strategy(self, strategy):
        return self.db.strategies.insert_one(strategy).inserted_id

    def get_strategies(self):
        return list(self.db.strategies.find({}, {'_id': 0}))

    def get_strategy(self, website):
        return self.db.strategies.find_one({"website": website}, {'_id': 0})

    def delete_strategy(self, website):
        return self.db.strategies.delete_one({"website": website})
