import requests
import time
from lxml import etree
import codecs

today_url = "https://cassandra.cerias.purdue.edu/CVE_changes/today.html"

def crawlToday():
    try:
        response = requests.get(today_url, timeout=(10, 10))
    except requests.exceptions.RequestException as e:
        print("Time Out")
        return False

    html = response.content.decode(response.encoding)

    page = etree.HTML(html)
    element_xpath = "/html/body/a/text()"
    today_updates = page.xpath(element_xpath)
    print(today_updates)

    # write a txt file for validation
    filename = '../ccpeMonitor/'+str(time.strftime("%m%d%H%M", time.localtime()))+'.txt'
    todayCrawled = codecs.open(filename, "w+")
    todayCrawled.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) )
    if len(today_updates)!=0:
        for update in today_updates:
            todayCrawled.write(update)

    return True

if __name__ == "__main__":

    while True:
        flag = crawlToday()
        while flag == False:
            sleep(10)
            flag = crawlToday()
        sleep(3600)





