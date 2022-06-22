import datetime
import time

from binance.client import Client
import pandas as pd


def parse(klines):
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
    df = pd.DataFrame(klines, columns=cols)
    df = df.drop(columns=['CloseTime', 'QuoteVolume', 'NumberTrades', 'TakerBuyBaseVolume', 'TakerBuyQuoteVolume', 'Ignore'])
    df[num_cols] = df[num_cols].apply(pd.to_numeric, errors='coerce')
    return df


def mtc(klines15, klines3, MM=28.45, TT=31.78):
    i = 0
    i3 = 0
    results = {}
    for kl15 in klines15['Open']:
        results[klines15['Date'][i]] = {
            'Open': kl15,
            'High': [],
            'Low': [],
            'Close': 0
        }
        i33 = 0
        while i33 < 5:
            if i3 >= len(klines3['Date']):
                i33 += 1
            elif klines3['Date'][i3] >= klines15['Date'][i]:
                results[klines15['Date'][i]]['Close'] = klines3['Close'][i3]
                results[klines15['Date'][i]]['High'].append(klines3['High'][i3])
                results[klines15['Date'][i]]['Low'].append(klines3['Low'][i3])
                i33 += 1
            i3 += 1
        results[klines15['Date'][i]]['High'] = max(results[klines15['Date'][i]]['High'])
        results[klines15['Date'][i]]['Low'] = min(results[klines15['Date'][i]]['Low'])

        i += 1
    BRS = (((list(klines15['Close'])[-1] - (sum(klines15['Low']) / len(klines15['Low']))) / ((sum(klines15['High']) / len(klines15['High'])) - (sum(klines15['Low']) / len(klines15['Low'])))) * 100) * 1
    M = 2.5 / 3 * MM + 0.5 / 3 * BRS
    T = 2.5 / 3 * TT + 0.5 / 3 * M
    C = 3 * M - 2 * T
    return BRS, M, T, C


def microTime(dt):
    return datetime.datetime.fromtimestamp(dt / 1000.0).strftime("%Y-%m-%d %H:%M:%S")


client = Client()
while True:
    limit = 11
    klines15 = client.futures_klines(symbol='BNBUSDT', interval=client.KLINE_INTERVAL_15MINUTE, limit=limit)
    klines3 = client.futures_klines(symbol='BNBUSDT', interval=client.KLINE_INTERVAL_3MINUTE, limit=(limit * 5))
    print(mtc(parse(klines15), parse(klines3), 20.25, 20.688))
    time.sleep(1)
