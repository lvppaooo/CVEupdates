from DailyUpdateByBooked import *
from DailyUpdateByCcpe import *
import time


if __name__ == "__main__":

    dailyUpdateByCcpe()
    dailyUpdateByBooked()
    time.sleep(60*60*24)