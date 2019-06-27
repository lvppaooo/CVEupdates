import pymysql
from config import *
from nvdSpider import nvdSpider


connection = pymysql.connect(host='localhost',
                       user=DB_user,
                       password=DB_password,
                       db=DB_name,
                       charset='utf8')

cursor = connection.cursor()

def dailyUpdateByBooked():

    cvenames = []

    sql = "select cveid from nvds where booked = 1"
    cursor.execute(sql)
    booked_cves = cursor.fetchall()


    if len(booked_cves)!=0:
        for booked_cve in booked_cves:
            if type(booked_cve) == tuple:
                cvenames.append(booked_cve[0])

    while len(cvenames)!=0:
        for cvename in cvenames:
            flag = nvdSpider(cvename)
            if flag == True:
                cvenames.remove(cvename)





