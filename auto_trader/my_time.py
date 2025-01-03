import time
import os
from datetime import datetime

import ntplib


def sync_ntp():
    client = ntplib.NTPClient()
    response = client.request('pool.ntp.org')
    t = datetime.fromtimestamp(response.tx_time)
    time_ntp = t.strftime("%m %d %H:%M:%S %Y")  # Mon Jul 05 13:58:39 2021
    print('NTP Time=' + str(time_ntp))
    # os.system('w32tm /resync')
    os.system('date ' + t.strftime("%x"))
    os.system('time ' + t.strftime("%X"))
