import time

import pandas as pd
from datetime import datetime

list = list(range(1, 10))
list.reverse()
print(list)
time.sleep(99999)

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


def microTime(dt):
    return datetime.fromtimestamp(dt / 1000.0).strftime("%Y-%m-%d %H:%M:%S")


def brs(klines3m, M=0, T=0, lastTime=0):
    # Klines 3M
    filterKlines3m = []
    high = []
    low = []
    for key, min3 in enumerate(klines3m):
        if len(filterKlines3m) == 0:
            filterKlines3m.append(min3)
            high.append(min3[2])
            low.append(min3[3])
        else:
            high.append(min3[2])
            low.append(min3[3])
            min3[2] = max(high)
            min3[3] = min(low)
            filterKlines3m.append(min3)
    klines3m = filterKlines3m
    if lastTime < klines3m[-1][0]:
        df3m = parse(klines3m)
        print(df3m)
        time.sleep(9999)

        BRS = ((list(df3m['Close'])[-1] - (sum(df3m['Low']) / len(df3m['Low']))) / ((sum(df3m['High']) / len(df3m['High'])) - (sum(df3m['Low']) / len(df3m['Low'])))) * 100
        M = 2.5 / 3 * M + 0.5 / 3 * BRS
        T = 2.5 / 3 * T + 0.5 / 3 * M
        C = 3 * M - 2 * T
        print("ANLIK:", M, T, BRS)
        if C > T:
            result = {
                'type': 'LONG',
                'side': 'BUY',
                'BRS': BRS,
                'M': M,
                'T': T,
                'C': C,
                'date': klines3m[-1][0],
                'dateFormat': microTime(klines3m[-1][0]),
                'Open': df3m['Open'][0],
                'High': max(df3m['High']),
                'Low': min(df3m['Low']),
                'Close': list(df3m['Close'])[-1],
            }
        else:
            result = {
                'type': 'SHORT',
                'side': 'SELL',
                'BRS': BRS,
                'M': M,
                'T': T,
                'C': C,
                'date': klines3m[-1][0],
                'dateFormat': microTime(klines3m[-1][0]),
                'Open': df3m['Open'][0],
                'High': max(df3m['High']),
                'Low': min(df3m['Low']),
                'Close': list(df3m['Close'])[-1],
            }
        return result
    else:
        return False


# client = Client()
# klines3m = client.futures_klines(symbol="BNBUSDT", interval="3m", limit=300)

M = -3
T = -30
# eskiden yeniye
klines = [
    [1656863100000, '214.790', '214.830', '214.320', '214.370', '3335.06', 1656863279999, '715616.22050', 909, '828.74', '177763.22120', '0'],
    [1656863280000, '214.380', '214.450', '214.310', '214.410', '952.53', 1656863459999, '204204.26040', 642, '653.65', '140133.58450', '0'],
    [1656863460000, '214.430', '214.580', '214.410', '214.440', '1494.78', 1656863639999, '320607.00320', 561, '720.37', '154508.64950', '0'],
    [1656863640000, '214.440', '214.440', '214.210', '214.370', '2446.38', 1656863819999, '524341.80220', 934, '1203.62', '257981.42960', '0'],
    [1656863820000, '214.370', '214.600', '214.360', '214.450', '2284.75', 1656863999999, '490028.16340', 910, '1459.22', '312985.85870', '0']
]
# for kl in klines:
#     print(microTime(kl[0]))
# print(parse(klines))
BRS = brs(klines, M, T)
print(BRS)
