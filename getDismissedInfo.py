import requests
import pymysql
from lxml import etree
from nvdSpider import nvdSpider

connection = pymysql.connect(host='47.103.76.55',
                            user = "root",
                            password = "123456",
                            db = "timo",
                            charset='utf8')

cursor = connection.cursor()

#update727_url = "https://cassandra.cerias.purdue.edu/CVE_changes/CVE.2019.07.html"
update817_url = "https://cassandra.cerias.purdue.edu/CVE_changes/CVE.2019.08.html"

response = requests.get(update817_url)

html = response.content.decode(response.encoding)

page = etree.HTML(html)
element_xpath = "//a/text()"
cve_names = page.xpath(element_xpath)
#print(cve_names)
print(cve_names[615:])
print("Length: ", len(cve_names))

to_be_crawled = cve_names[615:]


while len(to_be_crawled) != 0:
    for cvename in to_be_crawled:
        flag = nvdSpider(connection, "CVE-" + cvename)
        if flag == True:
            to_be_crawled.remove(cvename)

