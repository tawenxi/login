# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymysql
import os
import time
from urllib import request


class LoginPipeline:
    conn = None
    cursor = None

    def open_spider(self, spider):
        # 进行异常处理，可能会因为我们的疏忽或者数据库的更改造成连接失败，所以，我们要对这部分代码块进行异常捕捉
        if spider.name == 'document':
            try:
                # 连接数据库
                self.conn = pymysql.Connect(host='127.0.0.1', port=3306, user='root', password='', db='study8', charset='utf8')
                print('连接h 成功<<')
            except Exception as e:
                print(f'连接失败!!>>{e}')
                exit()  # 可以直接结束运行，按需求来设定

            pass


    def process_item(self, item, spider):

        if spider.name == 'document':
            print('#'*100)
            print(item)
            print('#'*100)


            # 创建游标
            self.cursor = self.conn.cursor()
            try:
                # 插入数据
                self.cursor.execute('INSERT INTO documents (bianhao,shijian,danwei,wenhao,biaoti,zhuangtai,leixing,docid,chengbanren) VALUES("{}", "{}","{}", "{}","{}", "{}","{}", "{}","{}")'.format(item['bianhao'], item['shijian'],item['danwei'], item['wenhao'],item['biaoti'], item['zhuangtai'],item['leixing'], item['docid'],'无'))
                print(f"数据<{item['docid']}>数据提交中...")
                # 数据提交到数据库
                self.conn.commit()
            except Exception as e:
                print(f">>存储失败>>数据<{item['docid']}>{e}")
                self.conn.rollback()
            return item
            pass

    def close_spider(self, spider):
        if spider.name == 'document':
            # 先关闭游标
            self.cursor.close()
            # 再关闭连接
            self.conn.close()
            pass


class BmwPipeline(object):
    def process_item(self, item, spider):
        pass
