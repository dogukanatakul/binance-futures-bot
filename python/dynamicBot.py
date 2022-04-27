import random
import time
import requests
from binance.client import Client
import pandas as pd
from datetime import datetime
import termtables as tt
from helper import config

url = config('API', 'SITE')


def get_diff(previous, current):
    try:
        if previous == current:
            percentage = 0
        elif previous < 0 and current < 0:
            percentage = ((previous - current) / min(previous, current)) * 100
        elif previous < 0 and current > 0:
            percentage = (((max(previous, current) - min(previous, current)) / max(previous, current)) * 100)
        elif previous > 0 and current < 0:
            percentage = (((max(previous, current) - min(previous, current)) / max(previous, current)) * 100) * -1
        elif previous > current:
            percentage = (((previous - current) / previous) * 100) * -1
        else:
            percentage = ((current - previous) / current) * 100
    except ZeroDivisionError:
        percentage = float('inf')
    return percentage


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


def get_kdj(kline):
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


def get_klines(client, parity, minute):
    minutes = {
        '1min': Client.KLINE_INTERVAL_1MINUTE,
        '5min': Client.KLINE_INTERVAL_5MINUTE,
        '15min': Client.KLINE_INTERVAL_15MINUTE,
        '30min': Client.KLINE_INTERVAL_30MINUTE,
        '1hour': Client.KLINE_INTERVAL_1HOUR,
        '4hour': Client.KLINE_INTERVAL_4HOUR
    }
    try:
        klineStatus = True
        kline = False
        while klineStatus:
            try:
                kline = client.get_klines(symbol=parity, interval=minutes[minute])
                klineStatus = False
            except Exception as e:
                print(str(e))
                time.sleep(2)
                klineStatus = True
        k, d, j = get_kdj(kline)
        if float(j) > float(d) and float(d) < float(k):
            return {
                'parity': parity,
                'K': k,
                'D': d,
                'J': j,
                'type': 'LONG',
                'side': 'BUY',
            }
        else:
            return {
                'parity': parity,
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


getBot = {
    'status': 0
}
while True:
    while getBot['status'] == 0 or getBot['status'] == 2:
        time.sleep(random.randint(3, 5))
        getBot = requests.post(url + 'get-order/new', headers={
            'neresi': 'dogunun+billurlari'
        }).json()
    print(getBot, "yeni emir")
    client = Client(getBot['api_key'], getBot['api_secret'], {"timeout": 40})

    dual = client.futures_get_position_mode()
    if not dual['dualSidePosition']:
        client.futures_change_position_mode(dualSidePosition=True)
    result = client.futures_change_leverage(symbol=getBot['parity'], leverage=getBot['leverage'])

    info = client.futures_exchange_info()
    fractions = {}
    for item in info['symbols']:
        fractions[item['symbol']] = item['quantityPrecision']

    # LONG: BUY | SHORT: SELL

    longStatus = False
    shortTrigger = 0
    lastQuantity = 0
    lastSide = False
    lastType = False
    J = 0
    cutOrder = False
    startJ = 0
    orderPrice = 0
    operationDelay = 0
    fakeReverse = 0
    fakeStatus = 0
    sameTest = {
        'K': 0,
        'D': 0,
        'J': 0
    }
    results = []
    operationLoop = True
    while operationLoop:
        getKline = get_klines(client, getBot['parity'], getBot['time'])
        if getKline['K'] != sameTest['K'] or getKline['D'] != sameTest['D'] or getKline['J'] != sameTest['J']:
            sameTest = {
                'K': getKline['K'],
                'D': getKline['D'],
                'J': getKline['J']
            }
            syncBot = requests.post(url + 'get-order/' + str(getBot['bot']), headers={
                'neresi': 'dogunun+billurlari'
            }).json()
            print(syncBot)
            for bt in syncBot.keys():
                getBot[bt] = syncBot[bt]
            if lastSide == False and lastType == False and getBot['status'] == 2:
                operationLoop = False
                setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                    'neresi': 'dogunun+billurlari'
                }, json={
                    'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'K': getKline['K'],
                    'D': getKline['D'],
                    'J': getKline['J'],
                    'action': 'STOP',
                }).status_code
            else:
                if shortTrigger >= getBot['short_trigger_min']:
                    if getKline['type'] == 'LONG' and longStatus == False:
                        if startJ == 0:
                            startJ = getKline['J']
                        elif startJ > getKline['J']:
                            startJ = getKline['J']
                            print(startJ, "BAŞLANGIÇ DEĞERİ DÜŞÜYOR!")
                        elif get_diff(startJ, getKline['J']) > getBot['start_diff']:
                            longStatus = True
                        else:
                            fakeStatus += 1
                            print("%" + str(get_diff(startJ, getKline['J'])) + " FARK BEKLENİYOR", startJ, getKline['J'])
                    elif getKline['type'] == 'SHORT' and longStatus == False:
                        print("SHORT DEVAM EDİYOR..")
                        shortTrigger = 0
                    elif not longStatus:
                        startJ = getKline['J']
                        setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                            'neresi': 'dogunun+billurlari'
                        }, json={
                            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'K': getKline['K'],
                            'D': getKline['D'],
                            'J': getKline['J'],
                            'action': 'LONG_WAITING',
                        }).status_code
                        if setBot != 200:
                            raise Exception('set_bot_fail')
                        print("LONG BEKLENİYOR..")
                    if longStatus:
                        if lastType == 'SHORT':
                            text = bcolors.FAIL + "{0}" + bcolors.ENDC
                        else:
                            text = bcolors.OKGREEN + "{0}" + bcolors.ENDC
                        if getKline:
                            if not lastType:
                                buyPrice = float(client.get_symbol_ticker(symbol=getBot['parity'])['price'])
                                lastQuantity = "{:0.0{}f}".format(float((getOrderBalance(client, getBot['source'], getBot['percent']) / buyPrice) * getBot['leverage']), fractions[getBot['parity']])
                                if float(lastQuantity) <= 0:
                                    raise Exception("Bakiye hatası")
                                lastSide = getKline['side']
                                lastType = getKline['type']
                                J = getKline['J']
                                cutOrder = False
                                setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                                    'neresi': 'dogunun+billurlari'
                                }, json={
                                    'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    'K': getKline['K'],
                                    'D': getKline['D'],
                                    'J': getKline['J'],
                                    'side': getKline['side'],
                                    'position_side': getKline['type'],
                                    'quantity': lastQuantity,
                                    'price': buyPrice,
                                    'action': 'OPEN',
                                }).status_code
                                if setBot != 200:
                                    raise Exception("set_bot_fail")
                                fakeReverse = 0
                                # client.futures_create_order(symbol=getBot['parity'], side=getKline['side'], type='MARKET', quantity=lastQuantity, positionSide=getKline['type'])
                            elif lastType != getKline['type']:
                                if operationDelay >= getBot['reverse_delay']:
                                    if lastSide != getKline['side']:
                                        operationDelay = 1
                                        buyPrice = float(client.get_symbol_ticker(symbol=getBot['parity'])['price'])
                                        if not cutOrder:
                                            setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                                                'neresi': 'dogunun+billurlari'
                                            }, json={
                                                'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                'K': getKline['K'],
                                                'D': getKline['D'],
                                                'J': getKline['J'],
                                                'side': lastSide,
                                                'position_side': lastType,
                                                'quantity': lastQuantity,
                                                'price': buyPrice,
                                                'action': 'CLOSE',
                                            }).status_code
                                            if setBot != 200:
                                                raise Exception("set_bot_fail")

                                            # client.futures_cancel_all_open_orders(symbol=getBot['parity'])
                                            # client.futures_create_order(symbol=getBot['parity'], side=getKline['side'], positionSide=lastType, type="MARKET", quantity=lastQuantity)

                                        lastQuantity = "{:0.0{}f}".format(float((getOrderBalance(client, getBot['source'], getBot['percent']) / buyPrice) * getBot['leverage']), fractions[getBot['parity']])
                                        if float(lastQuantity) <= 0:
                                            raise Exception("Bakiye hatası")
                                        if getBot['status'] == 2:
                                            operationLoop = False
                                            print("emir kapatıldı!")
                                        else:
                                            lastSide = getKline['side']
                                            lastType = getKline['type']
                                            J = getKline['J']
                                            cutOrder = False
                                            setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                                                'neresi': 'dogunun+billurlari'
                                            }, json={
                                                'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                'K': getKline['K'],
                                                'D': getKline['D'],
                                                'J': getKline['J'],
                                                'side': getKline['side'],
                                                'position_side': getKline['type'],
                                                'quantity': lastQuantity,
                                                'price': buyPrice,
                                                'action': 'OPEN',
                                            }).status_code
                                            if setBot != 200:
                                                raise Exception("set_bot_fail")
                                            # client.futures_create_order(symbol=getBot['parity'], side=getKline['side'], type='MARKET', quantity=lastQuantity, positionSide=getKline['type'])
                                            fakeReverse = 0
                                            print(text.format(lastType), text.format(" İŞLEM AÇILDI"))
                                    else:
                                        operationDelay = 1
                                        print("İŞLER KARIŞTI! DEVAM...")
                                else:
                                    print(getKline['side'], str(operationDelay) + ". DENEME")
                                    operationDelay += 1
                            else:
                                price = float(client.get_symbol_ticker(symbol=getBot['parity'])['price'])
                                if J < getKline['J'] and lastType == 'LONG':
                                    # J mevcuttan küçükse sınır miktarını güncelle
                                    J = getKline['J']
                                    fakeReverse = 0
                                    print("LONG DEĞERİ DEĞİŞTİ")
                                elif J > getKline['J'] and lastType == 'SHORT':
                                    # J mevcuttan büyükse sınır miktarını güncelle
                                    J = getKline['J']
                                    fakeReverse = 0
                                    print("SHORT DEĞERİ DEĞİŞTİ")

                                if lastType == 'LONG' and get_diff(getKline['J'], J) >= getBot['trigger_diff'] and cutOrder is False and price > buyPrice:
                                    if fakeReverse >= getBot['fake_reverse']:
                                        cutOrder = True
                                        buyPrice = float(client.get_symbol_ticker(symbol=getBot['parity'])['price'])
                                        setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                                            'neresi': 'dogunun+billurlari'
                                        }, json={
                                            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                            'K': getKline['K'],
                                            'D': getKline['D'],
                                            'J': getKline['J'],
                                            'side': "SELL",
                                            'position_side': "LONG",
                                            'quantity': lastQuantity,
                                            'price': buyPrice,
                                            'action': 'CLOSE_TRIGGER',
                                        }).status_code
                                        if setBot != 200:
                                            raise Exception("set_bot_fail")
                                        # client.futures_cancel_all_open_orders(symbol=getBot['parity'])
                                        # client.futures_create_order(symbol=getBot['parity'], side="SELL", positionSide="LONG", type="MARKET", quantity=lastQuantity)
                                    else:
                                        print("ORDER METER", str(fakeReverse))
                                        fakeReverse += 1
                                elif lastType == 'SHORT' and get_diff(J, getKline['J']) >= getBot['trigger_diff'] and cutOrder is False and price < buyPrice:
                                    if fakeReverse >= getBot['fake_reverse']:
                                        cutOrder = True
                                        buyPrice = float(client.get_symbol_ticker(symbol=getBot['parity'])['price'])
                                        setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                                            'neresi': 'dogunun+billurlari'
                                        }, json={
                                            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                            'K': getKline['K'],
                                            'D': getKline['D'],
                                            'J': getKline['J'],
                                            'side': "BUY",
                                            'position_side': "SHORT",
                                            'quantity': lastQuantity,
                                            'price': buyPrice,
                                            'action': 'CLOSE_TRIGGER',
                                        }).status_code
                                        if setBot != 200:
                                            raise Exception("set_bot_fail")
                                        # client.futures_cancel_all_open_orders(symbol=getBot['parity'])
                                        # client.futures_create_order(symbol=getBot['parity'], side="BUY", positionSide="SHORT", type="MARKET", quantity=lastQuantity)
                                    else:
                                        print("ORDER METER", str(fakeReverse))
                                        fakeReverse += 1
                                operationDelay = 1
                                if cutOrder:
                                    fakeStatus += 1
                                    print("BEKLİYOR:")
                                    if getBot['status'] == 2:
                                        operationLoop = False
                                        print("emir kapatıldı!")
                                else:
                                    fakeStatus += 1
                                    setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                                        'neresi': 'dogunun+billurlari'
                                    }, json={
                                        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        'K': getKline['K'],
                                        'D': getKline['D'],
                                        'J': getKline['J'],
                                        'side': lastSide,
                                        'position_side': lastType,
                                        'quantity': lastQuantity,
                                        'price': buyPrice,
                                        'action': 'CONTINUE',
                                    }).status_code
                                    if setBot != 200:
                                        raise Exception("set_bot_fail")
                                    print(text.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), text.format(lastType + " DEVAM EDİYOR"))
                else:
                    if getKline['type'] == 'SHORT':
                        shortTrigger += 1
                        print("SHORT TRIGGER ADD")
                    print("SHORT TRICKER")
                    setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                        'neresi': 'dogunun+billurlari'
                    }, json={
                        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'K': getKline['K'],
                        'D': getKline['D'],
                        'J': getKline['J'],
                        'action': 'SHORT_TRICKER',
                    }).status_code
        else:
            time.sleep(1)
