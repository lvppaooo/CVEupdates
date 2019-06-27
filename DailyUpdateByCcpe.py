import pymysql
from config import *
from nvdSpider import nvdSpider
import requests
from lxml import etree
import time
import logging


connection = pymysql.connect(host='localhost',
                       user=DB_user,
                       password=DB_password,
                       db=DB_name,
                       charset='utf8')

cursor = connection.cursor()

today_url = "https://cassandra.cerias.purdue.edu/CVE_changes/today.html"

def dailyUpdateByCcpe():

    logging.basicConfig(filename="dailyUpdate.log", filemode="w",
                        format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
                        datefmt="%d-%M-%Y %H:%M:%S", level=logging.INFO)

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
    num = len(cvenames)

    while len(cvenames)!=0:
        for cvename in cvenames:
            flag = nvdSpider("CVE-"+cvename)
            if flag == True:
                cvenames.remove(cvename)

    logging.info(str(num)+" CVEs updated")



