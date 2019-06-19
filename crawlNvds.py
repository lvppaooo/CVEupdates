import requests
from lxml import etree
from nvdSpider import nvdSpider
import pymysql
import random
import time


connection = pymysql.connect(host='localhost',
                       user='root',
                       password='123456',
                       db='timo',
                       charset='utf8')

cursor = connection.cursor()

sql = "select * from CVE where flag=0 order by Name Desc limit 100"
cursor.execute(sql)
results = cursor.fetchall()

while results!=[]:
    print(len(results), "to be crawled")
    for result in results:
        print(time.asctime(time.localtime(time.time()))," Crawling: ",result[0]) 
        crawl_flag = nvdSpider(result[0])
        if crawl_flag==True:
            sql = "update CVE set flag = 1 where Name = %s"
            cursor.execute(sql, (result[0]))
            connection.commit()
        else:
            pass
    sql = "select * from CVE where flag=0 order by Name Desc limit 100"
    cursor.execute(sql)
    results = cursor.fetchall()
   # sleep_time = 5*random.random()
   # time.sleep(sleep_time)

