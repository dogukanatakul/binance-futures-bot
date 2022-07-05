import time
import pandas as pd
from datetime import timedelta, datetime
from binance.client import Client

print(1657045440000 - (180000 * 2))
time.sleep(999)


def ceil_date(date, **kwargs):
    date = datetime.fromtimestamp(date / 1000.0).timestamp()
    secs = timedelta(**kwargs).total_seconds()
    return datetime.fromtimestamp(date + secs - date % secs).strftime("%d%H%M")


client = Client()
klines3m = client.futures_klines(symbol="BNBUSDT", interval="3m", limit=100)
parity = {
    'date': 0,
    'parity': 'BNBUSDT',
    'M': 66.94872,
    'T': 100.1118,
    'ceil': 0
}
ceilStatus = False
for m3 in klines3m:
    if ceil_date((m3[0] + 180000), minutes=15) != parity['ceil'] and parity['ceil'] != 0:
        parity['ceil'] = ceil_date((m3[0] + 180000), minutes=15)
        ceilStatus = True
    elif parity['ceil'] == 0:
        parity['ceil'] = ceil_date((m3[0] + 180000), minutes=15)
        ceilStatus = False
    else:
        ceilStatus = False
    print(ceil_date(m3[0], minutes=15), ceilStatus)
