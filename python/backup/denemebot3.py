import time, datetime, os, json
import pandas as pd
from binance.client import Client

i = 0


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
    i = 2
    # Klines 3M
    archKlines3M = klines3m
    klines3m.pop(-1)

    '''
    klines3mNew = []
    for key, min3 in enumerate(klines3m):
        if int(klines15m[-1][0]) <= int(min3[0]):
            klines3mNew.append(min3)
    klines3m = klines3mNew
    '''

    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%len ", len(klines3m))
    if len(klines3m) != 0:
        df3m = parse(klines3m)
        # Klines 3M END
        if (datetime.datetime.now().minute % 15 == 0):
            klines15m.pop(-1)
            klines15m.pop(-1)
        else:
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

    print("Mehmet Hoca")
    print(klines15m[-1])
    print("mehmet hoca bitti")
    if result['date'] == klines15m[-1][0]:
        i = 0
        return result
    else:
        print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO: ", len(df15m['Low']))
        BRS = ((list(df15m['Close'])[-1] - (sum(df15m['Low']) / len(df15m['Low']))) / ((sum(df15m['High']) / len(df15m['High'])) - (sum(df15m['Low']) / len(df15m['Low'])))) * 100
        M = (2.5 / 3) * M + (0.5 / 3) * BRS
        T = (2.5 / 3) * T + (0.5 / 3) * M
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

BRS = {
    'date': 0,
    'BRS': 0,
    'M': 10,
    'T': 10
}

lastDate = 0
oldBRS = 0
klines3m = []
onceki_M = BRS['M']
onceki_T = BRS['T']


def brsWrapper():
    global BRS
    global onceki_T
    global onceki_M
    global lastDate
    global oldBRS
    if (datetime.datetime.now().second % 35 == 0):
        if (i != 2):
            time.sleep(1)
            klines15m = client.futures_klines(symbol="BNBUSDT", interval="15m", limit=11)
            minNow = datetime.datetime.now().minute % 15
            minPerc = int(minNow / 3)
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print("MinNow: ", minNow)
            print("MinPerc: ", minPerc)
            print("Tarih:", datetime.datetime.now())

            if (datetime.datetime.now().minute % 15 == 0):
                klines15m = client.futures_klines(symbol="BNBUSDT", interval="15m", limit=12)
            if (minPerc == 0):
                klines3m = client.futures_klines(symbol="BNBUSDT", interval="3m", limit=6)
            if (minPerc == 1):
                klines3m = client.futures_klines(symbol="BNBUSDT", interval="3m", limit=2)
            elif (minPerc == 2):
                klines3m = client.futures_klines(symbol="BNBUSDT", interval="3m", limit=3)
            elif (minPerc == 3):
                klines3m = client.futures_klines(symbol="BNBUSDT", interval="3m", limit=4)
            elif (minPerc == 4):
                klines3m = client.futures_klines(symbol="BNBUSDT", interval="3m", limit=5)

            # TODO buraya al == 0 kontrolünü

            print(klines3m[-2])
            print(klines15m[-2])
            if (datetime.datetime.now().minute % 15 == 3 and oldBRS != 0):
                onceki_M = BRS['M']
                onceki_T = BRS['T']
            BRS = brs(klines15m, klines3m, M=onceki_M, T=onceki_T, result=BRS)

            if (oldBRS != 0):
                print("onceki M: ", onceki_M)
                print("onceki T: ", onceki_T)
            oldBRS = BRS['BRS']

            print("tüm değerler - ", BRS)
            # print("3m - ", klines3m)
            # print("15m - ", klines15m)

            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            return BRS


while True:
    brsWrapper()
