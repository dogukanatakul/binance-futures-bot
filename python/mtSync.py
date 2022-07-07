import requests, time, json, os, sys
from datetime import timedelta, datetime
import pandas as pd
from binance.client import Client
from helper import config


def microTime(dt):
    return datetime.fromtimestamp(dt / 1000.0).strftime("%Y-%m-%d %H:%M:%S")


def jsonData(bot, status='GET', data={}):
    if status == 'SET':
        with open(os.path.dirname(os.path.realpath(__file__)) + "/syncs/" + bot + '.json', 'w+') as outfile:
            outfile.write(json.dumps(data))
        return True
    elif status == 'DELETE':
        try:
            os.remove((os.path.dirname(os.path.realpath(__file__)) + "/syncs/" + bot + '.json'))
            return True
        except:
            return False
    else:
        if os.path.exists(os.path.dirname(os.path.realpath(__file__)) + "/syncs/" + bot + '.json'):
            return json.loads(open(os.path.dirname(os.path.realpath(__file__)) + "/syncs/" + bot + '.json', "r").read())
        else:
            return False


def ceil_date(date, **kwargs):
    date = datetime.fromtimestamp(date / 1000.0).timestamp()
    secs = timedelta(**kwargs).total_seconds()
    return datetime.fromtimestamp(date + secs - date % secs).strftime("%d%H%M")


def toExcel(df, BRS, M, T, C, oldM, oldT):
    dates = []
    for date in df['Date']:
        dates.append(microTime(date))
    resultItems = {
        'BRS': list(range(0, 10)),
        'BRSExcel': list(range(0, 10)),
        'M': list(range(0, 10)),
        'T': list(range(0, 10)),
        'oldM': list(range(0, 10)),
        'oldT': list(range(0, 10)),
        'C': list(range(0, 10)),
    }
    resultItems['BRS'].append(BRS)
    resultItems['BRSExcel'].append('=((E12-AVERAGE(D2:D12))/(AVERAGE(C2:C12)-AVERAGE(D2:D12))*100)*1')
    resultItems['M'].append(M)
    resultItems['T'].append(T)
    resultItems['oldM'].append(oldM)
    resultItems['oldT'].append(oldT)
    resultItems['C'].append(C)
    dfParse = {
        'Open': list(df['Open']),
        'High': list(df['High']),
        'Low': list(df['Low']),
        'Close': list(df['Close']),
        'Date': dates,
        'BRS': resultItems['BRS'],
        'BRSExcel': resultItems['BRSExcel'],
        'M': resultItems['M'],
        'T': resultItems['T'],
        'oldM': resultItems['oldM'],
        'oldT': resultItems['oldT'],
        'C': resultItems['C'],
    }
    df_json = pd.read_json(json.dumps(dfParse))
    df_json.to_excel(os.path.dirname(os.path.realpath(__file__)) + "/datas/" + dates[-1] + ".xlsx")
    print("EXPORT")
    return None


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


def brs(klines3mGroup, M=0, T=0, lastTime=0):
    # Klines 3M
    klines3mFilter = []
    for m3 in klines3mGroup:
        high = []
        low = []
        openPrice = 0
        filterKlines3m = []
        for min3 in m3:
            if len(filterKlines3m) == 0:
                filterKlines3m.append(min3)
                openPrice = min3[1]
                high.append(min3[2])
                low.append(min3[3])
            else:
                high.append(min3[2])
                low.append(min3[3])
                min3[1] = openPrice
                min3[2] = max(high)
                min3[3] = min(low)
                filterKlines3m.append(min3)
        klines3mFilter.append(filterKlines3m[-1])
    klines3m = klines3mFilter[-11:]
    df3m = parse(klines3m)
    if lastTime < klines3m[-1][0]:
        BRS = ((list(df3m['Close'])[-1] - (sum(df3m['Low']) / len(df3m['Low']))) / ((sum(df3m['High']) / len(df3m['High'])) - (sum(df3m['Low']) / len(df3m['Low'])))) * 100
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
                'date': klines3m[-1][0],
                'dateFormat': microTime(klines3m[-1][0]),
                'Open': list(df3m['Open'])[-1],
                'High': list(df3m['High'])[-1],
                'Low': list(df3m['Low'])[-1],
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
                'Open': list(df3m['Open'])[-1],
                'High': list(df3m['High'])[-1],
                'Low': list(df3m['Low'])[-1],
                'Close': list(df3m['Close'])[-1],
            }
        return result
    else:
        return False


ceilStatus = False
parities = []
while True:
    setBotWhile = True
    setBotCount = 0
    while setBotWhile:
        parities = requests.post(config('API', 'SITE') + 'mt-sync', headers={
            'neresi': 'dogunun+billurlari'
        })
        if parities.status_code == 200:
            setBotWhile = False
            parities = parities.json()
        elif setBotCount >= int(config('API', 'ERR_COUNT')):
            raise Exception('server_error')
        else:
            time.sleep(1)
            setBotCount += 1
    for parity in parities:
        try:
            BRS = {}
            updateStatus = False
            # 180000 : 3min
            # 900000 : 15min
            missingTime = int((int(time.time() * 1000.0) - parity['date']) / 180000)
            if missingTime >= 1:
                missingTimeSET = missingTime + (5 * 11)
                client = {}
                klines3m = []
                clientConnect = True
                clientConnectCount = 0
                while clientConnect:
                    try:
                        client = Client()
                        klines3m = client.futures_klines(symbol=parity['parity'], interval="3m", limit=missingTimeSET, requests_params={"timeout": 300, 'proxies': parity['proxy']})
                        clientConnect = False
                    except Exception as e:
                        clientConnectCount += 1
                        if ("Max retries exceeded" in str(e) or "Too many requests" in str(e) or "recvWindow" in str(e) or "Connection broken" in str(e) or "Connection aborted." in str(e) or "Please try again" in str(e)) and clientConnectCount < 3:
                            time.sleep(float(config('SETTING', 'TIME_SLEEP')))
                        elif "Way too many requests" in str(e) or "Read timed out." in str(e) or (3 <= clientConnectCount <= 6):
                            time.sleep(float(config('SETTING', 'TIME_SLEEP')))
                        else:
                            raise Exception(e)
                timeRange = list(range(1, (missingTime + 1)))
                timeRange.reverse()
                for tmRng in timeRange:
                    klines3mGroup = {}
                    for m3 in klines3m[:(tmRng * -1)]:
                        quarter = ceil_date(m3[0], minutes=15)
                        if quarter not in klines3mGroup:
                            klines3mGroup[quarter] = []
                            klines3mGroup[quarter].append(m3)
                        else:
                            klines3mGroup[quarter].append(m3)
                    klines3mGroup = klines3mGroup.values()
                    BRS = brs(klines3mGroup, parity['M'], parity['T'], parity['date'])
                    if BRS:
                        if ceil_date((BRS['date'] + 180000), minutes=15) != parity['ceil'] and parity['ceil'] != "0" and parity['ceil'] != 0:
                            parity['ceil'] = ceil_date((BRS['date'] + 180000), minutes=15)
                            ceilStatus = True
                        elif parity['ceil'] == "0" or parity['ceil'] == 0:
                            parity['ceil'] = ceil_date((BRS['date'] + 180000), minutes=15)
                            ceilStatus = False
                        else:
                            ceilStatus = False
                        for key, value in BRS.items():
                            if ceilStatus == False and (key == 'T' or key == 'M'):
                                print('atla')
                            elif key == 'ceil':
                                print('ceil_atla')
                            else:
                                parity[key] = value
                        parity['date'] = list(klines3mGroup)[-1][-1][0]
                        parity['CURRENT_M'] = BRS['M']
                        parity['CURRENT_T'] = BRS['T']
                        parity['SET_CEIL'] = ceil_date((BRS['date'] + 180000), minutes=15)
                        setBotWhile = True
                        setBotCount = 0
                        while setBotWhile:
                            jsonData(parity['parity'], 'SET', parity)
                            setBot = requests.post(config('API', 'SITE') + 'mt-sync', headers={
                                'neresi': 'dogunun+billurlari'
                            }, json=parity)
                            if setBot.status_code == 200:
                                print("gönderildi")
                                setBotWhile = False
                            elif setBotCount >= int(config('API', 'ERR_COUNT')):
                                raise Exception('server_error')
                            else:
                                time.sleep(1)
                                setBotCount += 1
        except Exception as exception:
            errBotWhile = True
            errBotCount = 0
            while errBotWhile:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                errBot = requests.post(config('API', 'SITE') + 'set-error', headers={
                    'neresi': 'dogunun+billurlari'
                }, json={
                    'bot': 'mtSync.py',
                    'errors': [
                        str(exc_type),
                        str(fname),
                        str(exc_tb.tb_lineno),
                        str(exception)
                    ]
                })
                if errBot.status_code == 200:
                    errBotWhile = False
                elif errBotCount >= int(config('API', 'ERR_COUNT')):
                    raise Exception('server_error')
                else:
                    time.sleep(1)
                    errBotCount += 1
