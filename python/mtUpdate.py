import json, os, datetime, requests
import time
import pandas as pd
from binance.client import Client
from helper import config

while True:
    time.sleep(5)
    parities = requests.post(config('API', 'SITE') + 'mt-sync', headers={
        'neresi': 'dogunun+billurlari'
    }).json()
    for parity in parities:

        # 180000 : 3min
        print(int(time.time() * 1000.0))
