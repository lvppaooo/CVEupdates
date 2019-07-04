from DailyUpdateByBooked import *
from DailyUpdateByCcpe import *
import time
import logging
from config import UPDATE_MODE


if __name__ == "__main__":




    while True:

        logging.basicConfig(filename="dailyUpdate.log", filemode="w",
                            format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
                            datefmt="%d-%M-%Y %H:%M:%S", level=logging.INFO)

        logging.info("Daily Update Start ————")

        connection = pymysql.connect(host='localhost',
                                     user=DB_user,
                                     password=DB_password,
                                     db=DB_name,
                                     charset='utf8')
       
        if UPDATE_MODE == "CCPE":
            dailyUpdateByCcpe(connection)
        elif UPDATE_MODE == "BOOKED":
            dailyUpdateByBooked(connection)
        else:
            pass

        logging.info("Daily Update Finished.")
        print(time.asctime(time.localtime(time.time()))+"Daily Update Finished")
        connection.close()
        #time.sleep(60*60*24)
