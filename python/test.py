import time, sys, os, requests, uuid, talib, numpy
from datetime import datetime
from binance.client import Client
import pandas as pd
import termtables as tt
from helper import config
from inspect import currentframe, getframeinfo

getBot = requests.post('http://127.0.0.1:8000/api/get-order/173abdab-9153-4e14-a9ec-1c382f7ae494', headers={
    'neresi': 'dogunun+billurlari'
}).json()
lastType = 'SHORT'
lastMAC = 'SHORT'


def mac_dema(kline, dema_short=12, dema_long=26, dema_signal=9, lastMAC=None):
    print(dema_short, dema_long, dema_signal)
    df = pd.DataFrame(kline)
    df.columns = ['Datetime',
                  'Open', 'High', 'Low', 'Close', 'volume',
                  'close_time', 'qav', 'num_trades',
                  'taker_base_vol', 'taker_quote_vol', 'ignore']
    df.index = [datetime.fromtimestamp(x / 1000.0) for x in df.close_time]
    df.drop(['close_time', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol', 'ignore'], axis=1, inplace=True)
    df["Close"] = pd.to_numeric(df["Close"], downcast="float")
    close = df['Close']
    close = list(filter(lambda v: v == v, close))
    MMEslowa = talib.EMA(numpy.asarray(close), timeperiod=dema_long)
    MMEslowb = talib.EMA(MMEslowa, timeperiod=dema_long)
    DEMAslow = ((2 * MMEslowa) - MMEslowb)

    MMEfasta = talib.EMA(numpy.asarray(close), timeperiod=dema_short)
    MMEfastb = talib.EMA(MMEfasta, timeperiod=dema_short)
    DEMAfast = ((2 * MMEfasta) - MMEfastb)

    LigneMACD = DEMAfast - DEMAslow
    MMEsignala = talib.EMA(LigneMACD, timeperiod=dema_signal)
    MMEsignalb = talib.EMA(MMEsignala, timeperiod=dema_signal)
    Lignesignal = ((2 * MMEsignala) - MMEsignalb)

    if LigneMACD[-2] <= Lignesignal[-2] and LigneMACD[-1] >= Lignesignal[-1]:
        dir = 'LONG'
    elif LigneMACD[-2] >= Lignesignal[-2] and LigneMACD[-1] <= Lignesignal[-1]:
        dir = 'SHORT'
    else:
        dir = lastMAC
    return dir


client = Client()
klines = client.futures_klines(symbol=getBot['parity'], interval=client.KLINE_INTERVAL_15MINUTE, limit=300)
lastMAC = mac_dema(klines, min(getBot['dema_short'], getBot['dema_long']) if lastType == 'LONG' else max(getBot['dema_short'], getBot['dema_long']), min(getBot['dema_short'], getBot['dema_long']) if lastType == 'SHORT' else max(getBot['dema_short'], getBot['dema_long']), 50, lastMAC)

print(lastMAC)
