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

''''
connection = pymysql.connect(host='localhost',
                       user='root',
                       password='root0303',
                       db='timo',
                       charset='utf8')

cursor = connection.cursor()
'''

'''
## crawl 14w+ NVDs

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
'''

## craw nvds updated in 2019.4-2019.5


# 1. crawl nvds updated in April

cassandra_april_url = "https://cassandra.cerias.purdue.edu/CVE_changes/CVE.2019.04.html"

try:
    response = requests.get(cassandra_april_url, timeout=(10, 10))
except requests.exceptions.RequestException as e:
    print("Time Out")

html = response.content.decode(response.encoding)

page = etree.HTML(html)
element_xpath = "/html/body/a/text()"
april_updates = page.xpath(element_xpath)

while len(april_updates)!=0:
    for ele in april_updates:
        flag = nvdSpider("CVE-"+ele)

        if flag == True:
            april_updates.remove(ele)
        print(time.asctime(time.localtime(time.time())), "April Updates " + str(len(april_updates)) + " to be Crawled")

# 2. crawl nvds updates in May
cassandra_april_url = "https://cassandra.cerias.purdue.edu/CVE_changes/CVE.2019.05.html"

try:
    response = requests.get(cassandra_april_url, timeout=(10, 10))
except requests.exceptions.RequestException as e:
    print("Time Out")

html = response.content.decode(response.encoding)

page = etree.HTML(html)
element_xpath = "/html/body/a/text()"
may_updates = page.xpath(element_xpath)

while len(may_updates)!=0:
    for ele in may_updates:
        flag = nvdSpider("CVE-"+ele)

        if flag == True:
            may_updates.remove(ele)
        print(time.asctime(time.localtime(time.time())), "May Updates " + str(len(may_updates)) + " to be Crawled")

# 3. crawl nvds updates in June
cassandra_april_url = "https://cassandra.cerias.purdue.edu/CVE_changes/CVE.2019.06.html"

try:
    response = requests.get(cassandra_april_url, timeout=(10, 10))
except requests.exceptions.RequestException as e:
    print("Time Out")

html = response.content.decode(response.encoding)

page = etree.HTML(html)
element_xpath = "/html/body/a/text()"
june_updates = page.xpath(element_xpath)

while len(june_updates)!=0:
    for ele in june_updates:
        flag = nvdSpider("CVE-"+ele)

        if flag == True:
            june_updates.remove(ele)
        print(time.asctime(time.localtime(time.time())), "June Updates " + str(len(june_updates)) + " to be Crawled")



