import time, datetime, os, json
import pandas as pd
from binance.client import Client


def microTime(dt):
    return datetime.datetime.fromtimestamp(dt / 1000.0).strftime("%Y-%m-%d %H:%M:%S")


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


def brs(klines15m, klines3m, M=0, T=0, result={}):
    # Klines 3M
    archKlines3M = klines3m
    klines3m.pop(-1)
    klines3mNew = []
    for key, min3 in enumerate(klines3m):
        if int(klines15m[-1][0]) <= int(min3[0]):
            klines3mNew.append(min3)
    klines3m = klines3mNew
    if len(klines3m) != 0:
        df3m = parse(klines3m)
        # Klines 3M END
        klines15m.pop(-1)
        klines15m.append([
            klines3m[-1][0],
            klines3m[0][1],
            max(df3m['High']),
            min(df3m['Low']),
            klines3m[-1][4],
            klines3m[-1][5],
            klines3m[-1][6],
            klines3m[-1][7],
            klines3m[-1][8],
            klines3m[-1][9],
            klines3m[-1][10],
            klines3m[-1][11],
        ])
    df15m = parse(klines15m)
    if result['date'] == klines15m[-1][0]:
        return result
    else:
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
M = 67.1234
T = 56.789
BRS = {
    'date': 0
}


lastDate = 0
while True:
    klines15m = client.futures_klines(symbol="BNBUSDT", interval="15m", limit=11)
    print(klines15m)
    time.sleep(9999)
    klines3m = client.futures_klines(symbol="BNBUSDT", interval="3m", limit=6)
    BRS = brs(klines15m, klines3m, M, T, BRS)
    M = BRS['M']
    T = BRS['T']
