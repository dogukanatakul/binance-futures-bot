import requests, time
import pandas as pd
from binance.client import Client
from helper import config


def parse(kline):
    cols = [
        'Date',
        'Open',
        'High',
        'Low',
        'Close',
        'Volume',
        'CloseTime',
        'QuoteVolume',
        'NumberTrades',
        'TakerBuyBaseVolume',
        'TakerBuyQuoteVolume',
        'Ignore'
    ]
    num_cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'Date']
    df = pd.DataFrame(kline, columns=cols)
    df = df.drop(columns=['CloseTime', 'QuoteVolume', 'NumberTrades', 'TakerBuyBaseVolume', 'TakerBuyQuoteVolume', 'Ignore'])
    df[num_cols] = df[num_cols].apply(pd.to_numeric, errors='coerce')
    return df


def brs(klines15m, M=0, T=0):
    # Klines 3M
    df15m = parse(klines15m)
    BRS = ((list(df15m['Close'])[-1] - (sum(df15m['Low']) / len(df15m['Low']))) / ((sum(df15m['High']) / len(df15m['High'])) - (sum(df15m['Low']) / len(df15m['Low'])))) * 100
    M = 2.5 / 3 * M + 0.5 / 3 * BRS
    T = 2.5 / 3 * T + 0.5 / 3 * M
    C = 3 * M - 2 * T
    if C > T:
        result = {
            'type': 'LONG',
            'side': 'BUY',
            'BRS': BRS,
            'M': M,
            'T': T,
            'C': C,
            'date': klines15m[-1][0]
        }
    else:
        result = {
            'type': 'SHORT',
            'side': 'SELL',
            'BRS': BRS,
            'M': M,
            'T': T,
            'C': C,
            'date': klines15m[-1][0]
        }
    return result


client = Client()
while True:
    parities = requests.post(config('API', 'SITE') + 'mt-sync', headers={
        'neresi': 'dogunun+billurlari'
    }).json()
    for parity in parities:
        BRS = {}
        klines15m = []
        updateStatus = False
        # 180000 : 3min
        # 900000 : 15min
        missingTime = int((int(time.time() * 1000.0) - parity['export_time']) / 900000)
        if missingTime > 1:
            missingTime += 11
            missingTime += 1  # Güncel 15dk silinecek
            klines15m = client.futures_klines(symbol=parity['parity'], interval=parity['time'], limit=missingTime)
            klines15m.pop(-1)
            if len(klines15m) > 11:
                klinesCount = len(klines15m) - 11
                for ii in range(0, klinesCount):
                    updateStatus = True
                    BRS = brs(klines15m[ii:(ii + 11)], parity['BRS_M'], parity['BRS_T'])
                    # print(BRS)
                    parity['BRS_M'] = BRS['M']
                    parity['BRS_T'] = BRS['T']
        if updateStatus:
            BRS['id'] = parity['id']
            BRS['date'] = klines15m[-1][0]
            req = requests.post(config('API', 'SITE') + 'mt-sync', headers={
                'neresi': 'dogunun+billurlari'
            }, json=BRS).json()
            time.sleep(15)
