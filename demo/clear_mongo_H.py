from pymongo import MongoClient

client = MongoClient('mongodb://172.16.7.20:27017')
db = client['crawlab_test']['domain_gcb_Hub_02112020']
db.drop()
