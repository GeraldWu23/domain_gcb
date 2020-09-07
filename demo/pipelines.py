import time
import codecs
import csv
#from spiders.db import db, col_name, task_id


class DemoPipeline(object):
    def __init__(self):
        pass
        # 创建MONGODB数据库链接
        # client = pymongo.MongoClient(host=host, port=port)
        # 指定数据库
        # mydb = client[dbname]
        # 存放数据的数据库表名
        # self.post1 = mydb[sheetname]

    def process_item(self, item, spider):
        #
        # with codecs.open('/home/tianer/data.csv', 'a', encoding='utf-8')as csvfile:
        #     # 写入
        #     write = csv.writer(csvfile)
        #     # 写入语法：write.writerow([写入的是列表])
        #     data = dict(item)
        #     now_time = time.ctime()
        #     write.writerow([data['url'], data['full_title'], now_time])

        return item
