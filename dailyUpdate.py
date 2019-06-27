from DailyUpdateByBooked import *
from DailyUpdateByCcpe import *
import time
import logging


if __name__ == "__main__":

    logging.basicConfig(filename="dailyUpdate.log", filemode="w", format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
                        datefmt="%d-%M-%Y %H:%M:%S", level=logging.INFO)

    while True:

        logging.info("Daily Update Start ————")
       
        dailyUpdateByCcpe()
       #dailyUpdateByBooked()
        logging.info("Daily Update Finished.")
        time.sleep(60*60*6)
