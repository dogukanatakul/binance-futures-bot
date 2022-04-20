import time
from binance.client import Client
import datetime
import pandas as pd
import asyncio
from datetime import datetime
import termtables as tt
import sys

client = Client("SjlxXktwDHd1h7Nrg9HnAQM4oJ7R8tu9H7joAEJM9mPc79RWkj0qDMviby1wb7Zq", "KWyjvXX4lkMBtlwIj9R4BIJkpLgYcfwNfFIiSUemojroJaEgDLgGsnz7rfb4CHYG", {"timeout": 40})


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


tokenList = [
    'ADA',
    'AVAX',
    'ATOM',
    'ETH',
    'SOL',
    'BNB',
    'SHIB',
    'XRP',
    'DOGE',
    'LTC',
    'SAND',
    'GALA',
    'FTM',
    'WAVES',
    'EOS',
    'VET',
    'LINK',
    'CHZ',
    'TRX',
    'ENJ',
    'IOST',
    'IOTA',
    'CRV',
    'SUSHI',
    '1INCH',
    'ALGO',
    'BCH',
    'ETC',
    'BAT',
    'HOT',
    'DENT',
    'DASH',
    'ZEC',
    'MATIC',
    'XLM',
    'XMR',
    'QTUM',
    'ZIL',
    'DOT',
    'NEAR',
    'REEF',
    'MANA',
    'APE',
    'GRT',
    'THETA',
    'SRM',
    'TOMO',
    'KSM',
    'BAKE',
    'ONE',
    'ARPA',
    'SXP',
    'BAND'
]


async def run_tasks(tasks):
    await asyncio.gather(*tasks)


def microTime(dt):
    return datetime.datetime.fromtimestamp(dt / 1000.0).strftime("%Y-%m-%d %H:%M:%S")


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


filterList = []


def get_klines(token, minute):
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
                kline = client.get_klines(symbol=token, interval=minutes[minute])
                klineStatus = False
            except Exception as e:
                print(str(e))
                time.sleep(2)
                klineStatus = True

        k, d, j = get_kdj(kline)
        if float(j) > float(d) and float(d) < float(k):
            return {
                'token': token,
                'K': k,
                'D': d,
                'J': j,
                'type': 'LONG',
                'side': 'BUY',
            }
        else:
            return {
                'token': token,
                'K': k,
                'D': d,
                'J': j,
                'type': 'SHORT',
                'side': 'SELL'
            }
    except Exception as e:
        print(token, str(e))
        return False


def getOrderBalance(currenty, percent):
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


dual = client.futures_get_position_mode()
if not dual['dualSidePosition']:
    client.futures_change_position_mode(dualSidePosition=True)
token = sys.argv[2]
money = "USDT"
crossX = 10
result = client.futures_change_leverage(symbol=token + money, leverage=crossX)

# LONG: BUY | SHORT: SELL

longStatus = False
shortTrigger = 0
shortTriggerMin = 10
operationDelay = 1
lastQuantity = 0
lastSide = ''
lastType = False
J = 0
cutOrder = False
startJ = 0
currentJ = 0
results = []
orderPrice = 0
operationDelayAmount = 3
orderMeter = 0
orderMeterCount = 2
percentPlay = 10
minute = sys.argv[1]

minutes = {
    '1min': 20,
    '5min': 10,
    '15min': 15,
    '30min': 3,
    '1hour': 7,
    '4hour': 5
}

startMinutes = {
    '1min': 15,
    '5min': 10,
    '15min': 15,
    '30min': 3,
    '1hour': 7,
    '4hour': 5
}
sameTest = {
    'K': 0,
    'D': 0,
    'J': 0
}
fakeStatus = 0

while True:
    getKline = get_klines(token + money, minute)
    if shortTrigger >= shortTriggerMin:
        if getKline['K'] != sameTest['K'] or getKline['D'] != sameTest['D'] or getKline['J'] != sameTest['J']:
            sameTest = {
                'K': getKline['K'],
                'D': getKline['D'],
                'J': getKline['J']
            }
            if getKline['type'] == 'LONG' and longStatus == False:
                if startJ == 0:
                    startJ = getKline['J']
                elif startJ > getKline['J']:
                    startJ = getKline['J']
                    # print(startJ, "BAŞLANGIÇ DEĞERİ DÜŞÜYOR!")
                elif get_diff(startJ, getKline['J']) > startMinutes[minute]:
                    longStatus = True
                else:
                    fakeStatus += 1
                    # print("%" + str(get_diff(startJ, getKline['J'])) + " FARK BEKLENİYOR", startJ, getKline['J'])
            elif getKline['type'] == 'SHORT' and longStatus == False:
                # print("SHORT DEVAM EDİYOR..")
                shortTrigger = 0
            elif not longStatus:
                startJ = getKline['J']
                # print("LONG BEKLENİYOR..")
            if longStatus:
                if lastType == 'SHORT':
                    text = bcolors.FAIL + "{0}" + bcolors.ENDC
                else:
                    text = bcolors.OKGREEN + "{0}" + bcolors.ENDC
                if getKline:
                    if not lastType:
                        buyPrice = float(client.get_symbol_ticker(symbol=token + money)['price'])
                        lastQuantity = int((getOrderBalance(money, percentPlay) / buyPrice) * crossX)
                        if lastQuantity <= 0:
                            raise Exception("Bakiye hatası")
                        lastSide = getKline['side']
                        lastType = getKline['type']
                        J = getKline['J']
                        cutOrder = False
                        results.append({
                            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'price': buyPrice,
                            'quantity': lastQuantity,
                            'side': getKline['side'],
                            'type': 'MARKET',
                            'action': 'OPEN'
                        })
                        terminalTable(results)
                        orderMeter = 0
                        # client.futures_create_order(symbol=token + money, side=getKline['side'], type='MARKET', quantity=lastQuantity, positionSide=getKline['type'])
                    elif lastType != getKline['type']:
                        if operationDelay > operationDelayAmount:
                            if lastSide != getKline['side']:
                                operationDelay = 1
                                buyPrice = float(client.get_symbol_ticker(symbol=token + money)['price'])
                                if not cutOrder:
                                    results.append({
                                        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        'price': buyPrice,
                                        'quantity': lastQuantity,
                                        'side': lastSide,
                                        'type': 'MARKET',
                                        'action': 'CLOSE'
                                    })
                                    terminalTable(results)
                                    # client.futures_cancel_all_open_orders(symbol=token + money)
                                    # client.futures_create_order(symbol=token + money, side=getKline['side'], positionSide=lastType, type="MARKET", quantity=lastQuantity)

                                lastQuantity = int((getOrderBalance(money, percentPlay) / buyPrice) * crossX)
                                if lastQuantity <= 0:
                                    raise Exception("Bakiye hatası")
                                lastSide = getKline['side']
                                lastType = getKline['type']
                                J = getKline['J']
                                cutOrder = False
                                results.append({
                                    'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    'price': buyPrice,
                                    'quantity': lastQuantity,
                                    'side': getKline['side'],
                                    'type': 'MARKET',
                                    'action': 'OPEN'
                                })
                                terminalTable(results)
                                # client.futures_create_order(symbol=token + money, side=getKline['side'], type='MARKET', quantity=lastQuantity, positionSide=getKline['type'])
                                orderMeter = 0
                                # print(text.format(lastType), text.format(" İŞLEM AÇILDI"))
                            else:
                                operationDelay = 1
                                # print("İŞLER KARIŞTI! DEVAM...")
                        else:
                            # print(getKline['side'], str(operationDelay) + ". DENEME")
                            operationDelay += 1
                    else:
                        price = float(client.get_symbol_ticker(symbol=token + money)['price'])
                        if J < getKline['J'] and lastType == 'LONG':
                            # J mevcuttan küçükse sınır miktarını güncelle
                            J = getKline['J']
                            orderMeter = 0
                            # print("LONG DEĞERİ DEĞİŞTİ")
                        elif J > getKline['J'] and lastType == 'SHORT':
                            # J mevcuttan büyükse sınır miktarını güncelle
                            J = getKline['J']
                            orderMeter = 0
                            # print("SHORT DEĞERİ DEĞİŞTİ")

                        if lastType == 'LONG' and get_diff(getKline['J'], J) >= minutes[minute] and cutOrder is False and price > buyPrice:
                            if orderMeter >= orderMeterCount:
                                cutOrder = True
                                buyPrice = float(client.get_symbol_ticker(symbol=token + money)['price'])
                                results.append({
                                    'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    'price': buyPrice,
                                    'quantity': lastQuantity,
                                    'side': 'BUY',
                                    'type': 'MARKET',
                                    'action': 'CLOSE_TRIGGER'
                                })
                                terminalTable(results)
                                # client.futures_cancel_all_open_orders(symbol=token + money)
                                # client.futures_create_order(symbol=token + money, side="SELL", positionSide="LONG", type="MARKET", quantity=lastQuantity)
                            else:
                                # print("ORDER METER", str(orderMeter))
                                orderMeter += 1
                        elif lastType == 'SHORT' and get_diff(J, getKline['J']) >= minutes[minute] and cutOrder is False and price < buyPrice:
                            if orderMeter >= orderMeterCount:
                                cutOrder = True
                                buyPrice = float(client.get_symbol_ticker(symbol=token + money)['price'])
                                results.append({
                                    'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    'price': buyPrice,
                                    'quantity': lastQuantity,
                                    'side': 'SELL',
                                    'type': 'MARKET',
                                    'action': 'CLOSE_TRIGGER'
                                })
                                terminalTable(results)
                                # client.futures_cancel_all_open_orders(symbol=token + money)
                                # client.futures_create_order(symbol=token + money, side="BUY", positionSide="SHORT", type="MARKET", quantity=lastQuantity)
                            else:
                                # print("ORDER METER", str(orderMeter))
                                orderMeter += 1
                        operationDelay = 1
                        if cutOrder:
                            fakeStatus += 1
                            # print("BEKLİYOR:")
                        else:
                            fakeStatus += 1
                            # print(text.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), text.format(lastType + " DEVAM EDİYOR"))
        else:
            time.sleep(1)
    else:
        if getKline['type'] == 'SHORT':
            shortTrigger += 1
            # print("SHORT TRIGGER ADD")
        # print("SHORT TRICKER")
