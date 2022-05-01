import random, time, sys, os, requests
from datetime import datetime
from binance.client import Client
import pandas as pd
import termtables as tt
from helper import config
from tillsonT3 import getSignal
import numpy as np

url = config('API', 'SITE')


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def kdj(kline):
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
    num_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    df = pd.DataFrame(kline, columns=cols)
    df = df.drop(columns=['CloseTime', 'QuoteVolume', 'NumberTrades', 'TakerBuyBaseVolume', 'TakerBuyQuoteVolume', 'Ignore'])
    df[num_cols] = df[num_cols].apply(pd.to_numeric, errors='coerce')
    low_list = df['Low'].rolling(9, min_periods=9).min()
    low_list.fillna(value=df['Low'].expanding().min(), inplace=True)
    high_list = df['High'].rolling(9, min_periods=9).max()
    high_list.fillna(value=df['High'].expanding().max(), inplace=True)
    rsv = (df['Close'] - low_list) / (high_list - low_list) * 100
    df_kdj = df.copy()
    df_kdj['K'] = pd.DataFrame(rsv).ewm(com=2).mean()
    df_kdj['D'] = df_kdj['K'].ewm(com=2).mean()
    df_kdj['J'] = 3 * df_kdj['K'] - 2 * df_kdj['D']
    return df_kdj.tail(1)['K'].item(), df_kdj.tail(1)['D'].item(), df_kdj.tail(1)['J'].item()


def get_kdj(klines):
    try:
        klineStatus = True
        while klineStatus:
            try:
                klineStatus = False
            except Exception as e:
                print(str(e))
                time.sleep(2)
                klineStatus = True
        k, d, j = kdj(klines)
        if float(j) > float(d) and float(d) < float(k):
            return {
                'K': k,
                'D': d,
                'J': j,
                'type': 'LONG',
                'side': 'BUY'
            }
        else:
            return {
                'K': k,
                'D': d,
                'J': j,
                'type': 'SHORT',
                'side': 'SELL'
            }
    except Exception as e:
        return False


def getOrderBalance(client, currenty, percent):
    minAmount = 10
    maxAmount = 134
    try:
        balance = client.futures_account_balance(asset=currenty)
        balance = next(x for x in balance if x["asset"] == currenty)
        percentBalance = float((float(balance['balance']) / 100) * percent)
        if percentBalance > maxAmount:
            percentBalance = maxAmount
        elif percentBalance < minAmount:
            percentBalance = minAmount
        return float(percentBalance)
    except:
        return False


def terminalTable(data):
    if len(data) > 0:
        header = list(data[0].keys())
        resultData = []
        for d in data:
            resultData.append(list(d.values()))
        tt.print(
            list(resultData),
            header=header,
        )


def getCoinHistory(klines):
    high = [float(entry[2]) for entry in klines]
    low = [float(entry[3]) for entry in klines]
    close = [float(entry[4]) for entry in klines]
    close_array = np.asarray(close)
    high_array = np.asarray(high)
    low_array = np.asarray(low)
    klinesMap = {
        "close": close_array,
        "high": high_array,
        "low": low_array
    }
    return klinesMap


getBot = {
    'status': 0
}
version = None
while True:
    while getBot['status'] == 0 or getBot['status'] == 2:
        getBot = requests.post(url + 'get-order/new', headers={
            'neresi': 'dogunun+billurlari'
        }).json()
        if version is not None and getBot['status'] == 0 and getBot['version'] != version:
            os.execl(sys.executable, sys.executable, *sys.argv)
        else:
            version = getBot['version']

    client = Client(str(getBot['api_key']), str(getBot['api_secret']), {"timeout": 40, 'proxies': getBot['proxy']})

    dual = client.futures_get_position_mode()
    if not dual['dualSidePosition']:
        client.futures_change_position_mode(dualSidePosition=True)
    result = client.futures_change_leverage(symbol=getBot['parity'], leverage=getBot['leverage'])
    info = client.futures_exchange_info()
    fractions = {}
    for item in info['symbols']:
        fractions[item['symbol']] = item['quantityPrecision']
    # LONG: BUY | SHORT: SELL
    sameTest = {
        'K': 0,
        'D': 0,
        'J': 0
    }
    operationLoop = True
    lastPrice = 0
    lastSide = 'HOLD'
    tillsonSide = 'HOLD'
    triggerStatus = False
    while operationLoop:
        try:
            minutes = {
                '1min': Client.KLINE_INTERVAL_1MINUTE,
                '5min': Client.KLINE_INTERVAL_5MINUTE,
                '15min': Client.KLINE_INTERVAL_15MINUTE,
                '30min': Client.KLINE_INTERVAL_30MINUTE,
                '1hour': Client.KLINE_INTERVAL_1HOUR,
                '4hour': Client.KLINE_INTERVAL_4HOUR
            }
            klines = client.get_klines(symbol=getBot['parity'], interval=minutes[str(getBot['time'])], limit=500)
            getKDJ = get_kdj(klines)
            if getKDJ['K'] != sameTest['K'] or getKDJ['D'] != sameTest['D'] or getKDJ['J'] != sameTest['J']:
                sameTest = {
                    'K': getKDJ['K'],
                    'D': getKDJ['D'],
                    'J': getKDJ['J']
                }

                # SYNC BOT
                syncBot = requests.post(url + 'get-order/' + str(getBot['bot']), headers={
                    'neresi': 'dogunun+billurlari'
                }).json()
                for bt in syncBot.keys():
                    getBot[bt] = syncBot[bt]
                # SYNC BOT END

                if lastSide == 'HOLD' and getBot['status'] == 2 and lastPrice == 0:
                    operationLoop = False
                    setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                        'neresi': 'dogunun+billurlari'
                    }, json={
                        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'K': getKDJ['K'],
                        'D': getKDJ['D'],
                        'J': getKDJ['J'],
                        'action': 'STOP',
                    }).status_code
                    if setBot != 200:
                        raise Exception('set_bot_fail')
                else:
                    # GET SIGNAL
                    history = getCoinHistory(klines)
                    signal = getSignal(history, float(getBot['volume_factor']), int(getBot['t3_length']), tillsonSide)
                    if signal == 'BUY' or signal == 'SELL':
                        tillsonSide = signal

                    # GET SIGNAL END
                    if tillsonSide == getKDJ['side'] and tillsonSide != lastSide:
                        lastPrice = float(client.get_symbol_ticker(symbol=getBot['parity'])['price'])
                        if lastSide != 'HOLD' and triggerStatus != True:
                            setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                                'neresi': 'dogunun+billurlari'
                            }, json={
                                'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                'K': getKDJ['K'],
                                'D': getKDJ['D'],
                                'J': getKDJ['J'],
                                'side': lastSide,
                                'price': lastPrice,
                                'action': 'CLOSE',
                            }).status_code
                            if setBot != 200:
                                raise Exception('set_bot_fail')
                        else:
                            triggerStatus = False
                        lastSide = tillsonSide
                        setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                            'neresi': 'dogunun+billurlari'
                        }, json={
                            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'K': getKDJ['K'],
                            'D': getKDJ['D'],
                            'J': getKDJ['J'],
                            'side': lastSide,
                            'price': lastPrice,
                            'action': 'OPEN',
                        }).status_code
                        if setBot != 200:
                            raise Exception('set_bot_fail')
                    elif tillsonSide != lastSide and signal != 'HOLD' and lastSide != 'HOLD' and triggerStatus != True:
                        triggerStatus = True
                        lastPrice = float(client.get_symbol_ticker(symbol=getBot['parity'])['price'])
                        setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                            'neresi': 'dogunun+billurlari'
                        }, json={
                            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'K': getKDJ['K'],
                            'D': getKDJ['D'],
                            'J': getKDJ['J'],
                            'side': lastSide,
                            'price': lastPrice,
                            'action': 'CLOSE_TRIGGER',
                        }).status_code
                        if setBot != 200:
                            raise Exception('set_bot_fail')
                    else:
                        if lastPrice == 0:
                            setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                                'neresi': 'dogunun+billurlari'
                            }, json={
                                'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                'K': getKDJ['K'],
                                'D': getKDJ['D'],
                                'J': getKDJ['J'],
                                'action': 'ORDER_START_WAITING',
                            }).status_code
                            if setBot != 200:
                                raise Exception('set_bot_fail')
            else:
                time.sleep(1)
        except Exception as exception:
            operationLoop = False
            getBot['status'] = 2
            print("emir kapatıldı!!")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            setBot = requests.post(url + 'set-error', headers={
                'neresi': 'dogunun+billurlari'
            }, json={
                'bot': getBot['bot'],
                'errors': [
                    str(exc_type),
                    str(fname),
                    str(exc_tb.tb_lineno),
                    str(exception)
                ]
            }).status_code
            if getBot['version'] != version:
                print("yeniden başlatma")
                os.execl(sys.executable, sys.executable, *sys.argv)
