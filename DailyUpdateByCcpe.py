import pymysql
from config import *
from nvdSpider import nvdSpider
import requests
from lxml import etree


connection = pymysql.connect(host='localhost',
                       user=DB_user,
                       password=DB_password,
                       db=DB_name,
                       charset='utf8')

cursor = connection.cursor()

today_url = "https://cassandra.cerias.purdue.edu/CVE_changes/today.html"

def dailyUpdateByCcpe():

    cvenames = []

    today_url = "https://cassandra.cerias.purdue.edu/CVE_changes/today.html"

    try:
        response = requests.get(today_url, timeout=(10, 10))
    except requests.exceptions.RequestException as e:
        print("Time Out")

    html = response.content.decode(response.encoding)

    page = etree.HTML(html)
    element_xpath = "/html/body/a/text()"
    cvenames = page.xpath(element_xpath)

    while len(cvenames)!=0:
        for cvename in cvenames:
            flag = nvdSpider("CVE-"+cvename)
            if flag == True:
                cvenames.remove(cvename)



