import time

from binance.client import Client
import datetime
import pandas as pd
import asyncio
import numpy as np
from datetime import datetime

client = Client("SjlxXktwDHd1h7Nrg9HnAQM4oJ7R8tu9H7joAEJM9mPc79RWkj0qDMviby1wb7Zq", "KWyjvXX4lkMBtlwIj9R4BIJkpLgYcfwNfFIiSUemojroJaEgDLgGsnz7rfb4CHYG", {"timeout": 40})


def get_change(current, previous):
    if current == previous:
        return 0
    try:
        return (abs(current - previous) / previous) * 100.0
    except ZeroDivisionError:
        return 0


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


def get_klines(token):
    try:
        kline = client.get_klines(symbol=token, interval=Client.KLINE_INTERVAL_15MINUTE)
        k, d, j = get_kdj(kline)
        if float(j) > float(d) and float(d) < float(k):
            return {
                'token': token,
                'K': k,
                'D': d,
                'J': j,
                'type': 'LONG',
                'action': 'BUY'
            }
        else:
            return {
                'token': token,
                'K': k,
                'D': d,
                'J': j,
                'type': 'SHORT',
                'action': 'SELL'
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


dual = client.futures_get_position_mode()
if not dual['dualSidePosition']:
    client.futures_change_position_mode(dualSidePosition=True)
token = "DOGE"
money = "USDT"
crossX = 20
result = client.futures_change_leverage(symbol=token + money, leverage=crossX)

# LONG: BUY | SHORT: SELL

longStatus = False
operationDelay = 1
lastPrice = 0
lastSide = ''
lastType = False
RECV_WINDOW = 6000000

while True:
    getKline = get_klines(token + money)
    print(getKline)
    if getKline['type'] == 'LONG':
        longStatus = True
    if longStatus:
        if lastType == 'SHORT':
            text = bcolors.FAIL + "{0}" + bcolors.ENDC
        else:
            text = bcolors.OKGREEN + "{0}" + bcolors.ENDC
        if getKline:
            if not lastType:
                buyPrice = float(client.get_symbol_ticker(symbol=token + money)['price'])
                quantity = int(getOrderBalance(money, 5) / buyPrice)
                lastPrice = (quantity * crossX)
                lastSide = getKline['action']
                lastType = getKline['type']
                client.futures_create_order(symbol=token + money, side=getKline['action'], type='MARKET', quantity=(quantity * crossX), positionSide=getKline['type'])
                print(text.format(lastType), text.format(" İŞLEM AÇILDI"))
            elif lastType != getKline['type']:
                if operationDelay > 10:
                    if lastSide != getKline['action']:
                        operationDelay = 1
                        client.futures_cancel_all_open_orders(symbol=token + money)
                        client.futures_create_order(symbol=token + money, side=getKline['action'], positionSide=lastType, type="MARKET", quantity=lastPrice)
                        print(text.format(lastType), text.format(" İŞLEM KAPATILDI"))
                        buyPrice = float(client.get_symbol_ticker(symbol=token + money)['price'])
                        quantity = int(getOrderBalance(money, 5) / buyPrice)
                        lastPrice = (quantity * crossX)
                        lastSide = getKline['action']
                        lastType = getKline['type']
                        client.futures_create_order(symbol=token + money, side=getKline['action'], type='MARKET', quantity=(quantity * crossX), positionSide=getKline['type'])
                        print(text.format(lastType), text.format(" İŞLEM AÇILDI"))
                    else:
                        operationDelay = 1
                        print("İŞLER KARIŞTI! DEVAM...")
                else:
                    print(getKline['action'], str(operationDelay) + ". DENEME")
                    operationDelay += 1
            else:
                operationDelay = 1
                print(text.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), text.format(lastType + " DEVAM EDİYOR"))
