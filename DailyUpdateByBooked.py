import pymysql
from config import *
from nvdSpider import nvdSpider
import logging


def dailyUpdateByBooked(connection):

    cursor = connection.cursor()

    logging.basicConfig(filename="dailyUpdate.log", filemode="w",
                        format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
                        datefmt="%d-%M-%Y %H:%M:%S", level=logging.INFO)

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
            flag = nvdSpider(connection, cvename)
            if flag == True:
                cvenames.remove(cvename)





