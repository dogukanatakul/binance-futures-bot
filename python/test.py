from binance.client import Client
import pandas as pd
import datetime as dt
import talib as ta
import talib, time, numpy

client = Client()




lastCE = None
lastMAC = None
while True:
    print()
    lastMAC = MACDEMA(client.futures_klines(symbol="BTCUSDT", interval=client.KLINE_INTERVAL_1MINUTE), courte=10, longue=5, signal=9, lastMAC=lastMAC)
    print(lastMAC)
    time.sleep(1)
