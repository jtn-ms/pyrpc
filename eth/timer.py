import time
from constants import ETH_BLK_TIME

def eth_timer():
    while 1:
        time.sleep(ETH_BLK_TIME)