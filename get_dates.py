import requests
import pymysql
from lxml import etree
import datetime as dt
import multiprocessing as mp

connection = pymysql.connect(host='47.103.76.55',
                       user='root',
                       password='123456',
                       db='timo',
                       charset='utf8')


def getDates(connection):

    while True:

        sql = "select cveid from nvds where published_date is null and last_modified is null"
        cursor = connection.cursor()
        cursor.execute(sql)
        try:
            cveid = cursor.fetchone()[0]
        except:
            break

        print(cveid)

        url = "https://nvd.nist.gov/vuln/detail/" + cveid
        try:
            response = requests.get(url, timeout=(10, 10))
        except requests.exceptions.RequestException as e:
            print("Exception: ", e)
            print(cveid, "to be crawled")
            continue

        html = response.content.decode(response.encoding)
        page = etree.HTML(html)

        published_date_xpath = "//*[@id=\"p_lt_WebPartZone1_zoneCenter_pageplaceholder_p_lt_WebPartZone1_zoneCenter_VulnerabilityDetail_VulnFormView\"]//div/div[2]/div/span[1]/text()"
        published_date = page.xpath(published_date_xpath)

        #print("published date: ", published_date)

        last_modified_xpath = "//*[@id=\"p_lt_WebPartZone1_zoneCenter_pageplaceholder_p_lt_WebPartZone1_zoneCenter_VulnerabilityDetail_VulnFormView\"]//div/div[2]/div/span[2]/text()"
        last_modified_date = page.xpath(last_modified_xpath)
        #print("last modified: ", last_modified_date)

        if len(published_date) != 0:
            string_published_date = published_date[0]

        if len(last_modified_date) != 0:
            string_last_modified = last_modified_date[0]

        published_year = int(string_published_date.split("/")[-1])
        published_month = int(string_published_date.split("/")[0])
        published_day = int(string_published_date.split("/")[1])

        published_date = dt.datetime(published_year, published_month, published_day)

        lm_year = int(string_last_modified.split("/")[-1])
        lm_month = int(string_last_modified.split("/")[0])
        lm_day = int(string_last_modified.split("/")[1])

        last_modified_date = dt.datetime(lm_year, lm_month, lm_day)
        print(published_date)
        print(last_modified_date)


        update_sql = "update nvds set published_date=%s, last_modified=%s where cveid=%s"
        cursor.execute(update_sql, (published_date, last_modified_date, cveid))
        connection.commit()

if __name__=="__main__":

    getDates(connection)

