# encoding:utf-8
import requests
from lxml import etree
import codecs
import json
import pymysql
import time
import random
import datetime as dt
from config import * 
import time
import logging
import pylint
'''
VULinfo

idVULinfo: INT, autoIncreasnig，
CVEID: VARCHAR
description: TEXT
priority: VARCHAR
solutionStatus: VARCHAR
attackVector: VARCHAR
impact: TEXT
affectedComponent: TEXT (dynamic)
solutions: VARCHAR
vendorAdvisories: TEXT
references: TEXT
'''



def nvdSpider(connection, CVEname):
    logging.basicConfig(filename="dailyUpdate.log", filemode="w",
                        format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
                        datefmt="%d-%M-%Y %H:%M:%S", level=logging.INFO)
    print(time.asctime(time.localtime(time.time()))+": Crawling "+CVEname)
    url = "https://nvd.nist.gov/vuln/detail/"+CVEname
    #print("url: ", url)

    description=''
    priority=''
    solutionStatus=''
    attackVector=''
    impact=''
    affectedComponents=''
    solutions=[]
    vendorAdvisories=''
    references=[]
    booked=None
    published_date = None
    last_modified_date = None


    try:
        response = requests.get(url, timeout=(10, 10))
    except requests.exceptions.RequestException as e:
        print(CVEname, "Time Out")
        return False
    html = response.content.decode(response.encoding)

    #write a html file for validation
    #nvdCrawled = codecs.open('nvd.html', "w+")
    #for line in html:
    #   nvdCrawled.write(line)

    page = etree.HTML(html)

    desXpath = "//*[@data-testid=\"vuln-description\"]/text()"
    try:
        description = page.xpath(desXpath)[0]
    except IndexError:
        pass
    #print("Description: ", description)

    priorityXpath = "//*[@data-testid=\"vuln-cvssv3-base-score-severity\"]/text()"
    try:
        priority = page.xpath(priorityXpath)[0]
    except IndexError:
        priorityXpath = "//*[@id=\"p_lt_WebPartZone1_zoneCenter_pageplaceholder_p_lt_WebPartZone1_zoneCenter_VulnerabilityDetail_VulnFormView_Vuln2CvssPanel\"]/p[1]/a/span[2]/text()"
        try:
            priority = page.xpath(priorityXpath)[0]
        except IndexError:
            pass
        pass

    #print("Priority: ", priority)

    attackVectorXpath = "//*[@data-testid=\"vuln-cvssv3-av\"]/text()"
    try:
        attackVector = page.xpath(attackVectorXpath)[0]
    except IndexError:
        attackVectorXpath = "//*[@id=\"p_lt_WebPartZone1_zoneCenter_pageplaceholder_p_lt_WebPartZone1_zoneCenter_VulnerabilityDetail_VulnFormView_Vuln2CvssPanel\"]/p[2]/span[1]/text()"
        try:
            attackVector = page.xpath(attackVectorXpath)[0]
        except IndexError:
            pass
        pass
    attackVector = attackVector.replace(' ', '')
    attackVector = attackVector.replace('\n', '')
    attackVector = attackVector.replace('\r', '')
    #print("attackVector: ", attackVector)

    impactXpath = "//*[@data-testid=\"vuln-cvssv2-additional\"]/text()"
    impacts = page.xpath(impactXpath)

    for ele in impacts:
        ele = ele.strip()
        impact+=ele
        impact+="\n"
    #print("impact: ", impact)

    #affectedComponentsXpath = "//*[@id=\"config-div-1\"]//b/text()"
    configurationsXpath = "//*[@id=\"p_lt_WebPartZone1_zoneCenter_pageplaceholder_p_lt_WebPartZone1_zoneCenter_VulnerabilityDetail_VulnFormView_VulnConfigurationsDiv\"]/div"
    configurations = page.xpath(configurationsXpath)

    for conf in configurations:

        conf_text = etree.tostring(conf)
        conf_text_string = conf_text.decode(response.encoding)
        #print(conf_text_string)
        conf_page = etree.HTML(conf_text_string)
        conf_eles = conf_page.xpath('//td/b/text()')
        #print("conf_eles: ",conf_eles)
    #print("afx: ",etree.tostring(ele))
    #print("afx: ", conf_eles)
        for conf_ele in conf_eles:
            if conf_ele.startswith("cpe"):
                conf_ele = conf_ele[10:]
                conf_ele = conf_ele.replace('*', '')
                conf_ele = conf_ele.replace(':', ' ')
                conf_ele = conf_ele.strip()
                affectedComponents+=conf_ele
                affectedComponents+=";"
        #print("affectedComponnet: ", affectedComponents)
    #print(len(affectedComponents))

   # print("affectedComponents: ", affectedComponents)
    cpeurisNameXpath = "//small/a/@data-cpe-list-toggle"
    cpeurisName = page.xpath(cpeurisNameXpath)
    for name in cpeurisName:
        subaffectedComponents = getCpeUris(name)
        for ele in subaffectedComponents:
            if ele.startswith("cpe"):
                ele = ele[10:]
                ele = ele.replace('*', '')
                ele = ele.replace(':', ' ')
                ele = ele.strip()
                affectedComponents+=ele
                affectedComponents+=";"


    refTableXpath = "//*[@id=\"p_lt_WebPartZone1_zoneCenter_pageplaceholder_p_lt_WebPartZone1_zoneCenter_VulnerabilityDetail_VulnFormView_VulnHyperlinksPanel\"]/table//tbody/tr"
    refTable = page.xpath(refTableXpath)
    ref_hplinks = []
    ref_resources = []
    references = []
    for ele in refTable:
        ss = etree.tostring(ele).decode(response.encoding)
       # print(ss)
        href_xpath = "//td/a/@href"
        label_xpath = "//td/span/text()"
        tableEle = etree.HTML(ss)
        hrefs = tableEle.xpath(href_xpath)
        for href in hrefs:
            references.append(href)

        ref_hplinks.append(hrefs)
        labels = tableEle.xpath(label_xpath)
        if 'Vendor Advisory' in labels:
            vendorAdvisories = hrefs[0]
            solutions = labels
            solutionStatus = 'Official Fix'

        ref_resources.append(labels)


    current_time = dt.datetime.now()
    current_time = current_time.strftime("%Y-%m-%d %H:%M:00")

    cursor = connection.cursor()

    sql = "select * from nvds where cveid=%s"
    cursor.execute(sql, (CVEname, ))
    results = cursor.fetchall()
    #print("results: ", results)

    published_date_xpath = "//*[@id=\"p_lt_WebPartZone1_zoneCenter_pageplaceholder_p_lt_WebPartZone1_zoneCenter_VulnerabilityDetail_VulnFormView\"]//div/div[2]/div/span[1]/text()"
    published_date = page.xpath(published_date_xpath)

    #print("published date: ", published_date)

    last_modified_xpath = "//*[@id=\"p_lt_WebPartZone1_zoneCenter_pageplaceholder_p_lt_WebPartZone1_zoneCenter_VulnerabilityDetail_VulnFormView\"]//div/div[2]/div/span[2]/text()"
    last_modified_date = page.xpath(last_modified_xpath)
    #print("last modified: ", last_modified_date)

    if len(published_date)!=0:
        string_published_date = published_date[0]

    if len(last_modified_date)!=0:
        string_last_modified = last_modified_date[0]

    published_year = int(string_published_date.split("/")[-1])
    published_month = int(string_published_date.split("/")[0])
    published_day = int(string_published_date.split("/")[1])

    published_date = dt.datetime(published_year, published_month, published_day)


    lm_year = int(string_last_modified.split("/")[-1])
    lm_month = int(string_last_modified.split("/")[0])
    lm_day = int(string_last_modified.split("/")[1])

    last_modified_date = dt.datetime(lm_year, lm_month, lm_day)
    #print(published_date)
    #print(last_modified_date)

    if len(results)!=0:
        stored_info = results[0]
        print(stored_info)
        print(str((results[0][0], CVEname, description, priority, str(solutionStatus), attackVector, str(impact), str(affectedComponents), str(solutions), str(vendorAdvisories), str(references), results[0][-2], results[0][-1])))
    #print(str((results[0][0], CVEname, description, priority, solutionStatus, attackVector, str(impact), affectedComponents, solutions, vendorAdvisories, references, results[0][-2], results[0][-1])))
        if stored_info == (results[0][0], CVEname, description, priority, str(solutionStatus), attackVector, str(impact), str(affectedComponents), str(solutions), str(vendorAdvisories), str(references), results[0][-2], results[0][-1]):
            logging.info("Booked "+str(CVEname)+" has not been updated")
            #print("No Change")
            return True

    if len(results) != 0:
        booked = results[0][-3]

        sql = "update nvds set description=%s, priority=%s, solution_status=%s, attack_vector=%s, impact=%s, affected_components=%s, solutions=%s, vendor_advisories=%s, hyperlink_references=%s, create_date=%s, booked=%s, published_date=%s, last_modified=%s where cveid=%s"
        cursor.execute(sql, (
        description, priority, str(solutionStatus), attackVector, str(impact), str(affectedComponents),
        str(solutions), str(vendorAdvisories), str(references), current_time, booked, published_date, last_modified_date, CVEname))
        connection.commit()
    else:
        sql = "insert into nvds (cveid, description, priority, solution_status, attack_vector, impact, affected_components, solutions, vendor_advisories, hyperlink_references, create_date, booked, published_date, last_modified) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (
        CVEname, description, priority, str(solutionStatus), attackVector, str(impact), str(affectedComponents),
        str(solutions), str(vendorAdvisories), str(references), current_time, booked, published_date, last_modified_date))
        connection.commit()

    cursor.close()
    logging.info(CVEname+" crawling finished")
   # sleep_time = random.random()
   # time.sleep(sleep_time)
    return True




def getCpeUris(cpeFactId):

    url = 'https://nvd.nist.gov/NVD/Services/CpeRangeServices.ashx?cpeFactId='+cpeFactId+'&resultsPerPage=50'
    try:
        response = requests.get(url, timeout=(3, 7))
        response_content = response.content.decode(response.encoding)
        response_json = json.loads(response_content)
        cpeUris = []
        for i in range(len(response_json["cpes"]["cpes"])):
            cpeUris.append(response_json["cpes"]["cpes"][i]["cpeUri"])
        return cpeUris
    except Exception as e:
        print("Exception", e)
        return []

#uris = getCpeUris("5082901")
#print(uris)




