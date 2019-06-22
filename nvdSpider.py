# encoding:utf-8
import requests
from lxml import etree
import codecs
import json
import pymysql
import time
import random
import datetime as dt

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


connection = pymysql.connect(host='localhost',
                       user='root',
                       password='123456',
                       db='timo',
                       charset='utf8')

'''
connection = pymysql.connect(host='localhost',
                       user='root',
                       password='root0303',
                       db='timo',
                       charset='utf8')
'''

def nvdSpider(CVEname):

    url = "https://nvd.nist.gov/vuln/detail/"+CVEname
    print("url: ", url)

    description=''
    priority=''
    solutionStatus=''
    attackVector=''
    impact=''
    affectedComponents=''
    solutions=[]
    vendorAdvisories=''
    references=[]
    booked=0

    try:
        response = requests.get(url, timeout=(10, 10))
    except requests.exceptions.RequestException as e:
        print(CVEname, "Time Out")
        return False
    html = response.content.decode(response.encoding)

    #write a html file for validation
    nvdCrawled = codecs.open('nvd.html', "w+")
    for line in html:
        nvdCrawled.write(line)

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




    #print("vendorAdvisories:", vendorAdvisories)
    #print("solutions: ", solutions)
    #print("solutionStatus: ", solutionStatus)
    #print("references: ", references)
    #print(len(attackVector))
    #print(type(attackVector))
    current_time = dt.datetime.now()
    current_time = current_time.strftime("%Y-%m-%d %H:%M:00")

    ##DATABASE UPDATE RULES:



    cursor = connection.cursor()

    sql = "select * from nvds where cveid=%s"
    cursor.execute(sql, (CVEname, ))
    results = cursor.fetchall()
    if len(results) != 0:
        booked = results[0][-1]

        sql = "update nvds set description=%s, priority=%s, solution_status=%s, attack_vector=%s, impact=%s, affected_components=%s, solutions=%s, vendor_advisories=%s, hyperlink_references=%s, create_date=%s, booked=%s where cveid=%s"
        cursor.execute(sql, (
        description, priority, str(solutionStatus), attackVector, str(impact), str(affectedComponents),
        str(solutions), str(vendorAdvisories), str(references), current_time, booked, CVEname))
        connection.commit()
    else:
        sql = "insert into nvds (cveid, description, priority, solution_status, attack_vector, impact, affected_components, solutions, vendor_advisories, hyperlink_references, create_date, booked) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (
        CVEname, description, priority, str(solutionStatus), attackVector, str(impact), str(affectedComponents),
        str(solutions), str(vendorAdvisories), str(references), current_time, booked))
        connection.commit()

    cursor.close()
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
    except:
        return []

#uris = getCpeUris("5082901")
#print(uris)



#nvdSpider('CVE-2019-11362')
