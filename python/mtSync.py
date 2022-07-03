import requests, time
from datetime import timedelta, datetime
import pandas as pd
from binance.client import Client
from helper import config


def microTime(dt):
    return datetime.fromtimestamp(dt / 1000.0).strftime("%Y-%m-%d %H:%M:%S")


def ceil_date(date, **kwargs):
    date = datetime.fromtimestamp(date / 1000.0).timestamp()
    secs = timedelta(**kwargs).total_seconds()
    return datetime.fromtimestamp(date + secs - date % secs).strftime("%d%H%M")


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


client = Client()
while True:
    parities = requests.post(config('API', 'SITE') + 'mt-sync', headers={
        'neresi': 'dogunun+billurlari'
    }).json()
    for parity in parities:
        BRS = {}
        updateStatus = False
        # 180000 : 3min
        # 900000 : 15min
        missingTime = int((int(time.time() * 1000.0) - parity['date']) / 180000)
        if missingTime > 1:
            missingTime += 5
            client = {}
            clientConnect = True
            clientConnectCount = 0
            while clientConnect:
                try:
                    client = Client(requests_params={"timeout": 300, 'proxies': parity['proxy']})
                    clientConnect = False
                except Exception as e:
                    clientConnectCount += 1
                    if ("Max retries exceeded" in str(e) or "Too many requests" in str(e) or "recvWindow" in str(e) or "Connection broken" in str(e) or "Please try again" in str(e)) and clientConnectCount < 3:
                        time.sleep(float(config('SETTING', 'TIME_SLEEP')))
                    elif "Way too many requests" in str(e) or "Read timed out." in str(e) or (3 <= clientConnectCount <= 6):
                        proxy = requests.post(config('API', 'SITE') + 'mt-sync-proxy', headers={
                            'neresi': 'dogunun+billurlari'
                        }).json()
                        if proxy['status'] == 'success':
                            parity['proxy'] = proxy['proxy']
                        else:
                            raise Exception(e)
                    else:
                        raise Exception(e)
            del parity['proxy']
            klines3m = client.futures_klines(symbol=parity['parity'], interval="3m", limit=missingTime)
            klines3m.pop(-1)
            klines3mGroup = {}
            for m3 in klines3m:
                quarter = ceil_date(m3[0], minutes=15)
                if quarter not in klines3mGroup:
                    klines3mGroup[quarter] = []
                    klines3mGroup[quarter].append(m3)
                else:
                    klines3mGroup[quarter].append(m3)
            for min3 in klines3mGroup:
                groupCount = 0
                for klGroup in klines3mGroup[min3]:
                    groupCount += 1
                    BRS = brs(klines3mGroup[min3][0:groupCount], parity['M'], parity['T'], parity['date'])
                    if BRS != False:
                        for key, value in BRS.items():
                            parity[key] = value
                        req = requests.post(config('API', 'SITE') + 'mt-sync', headers={
                            'neresi': 'dogunun+billurlari'
                        }, json=parity).json()
                        if req['status'] == 'fail':
                            print("HATA")
