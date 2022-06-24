import json, os, datetime
import pandas as pd
from binance.client import Client

symbols = [
    'BNBUSDT',
]


def microTime(dt):
    return datetime.datetime.fromtimestamp(dt / 1000.0).strftime("%Y-%m-%d %H:%M:%S")


for symbol in symbols:
    client = Client()
    klines = client.futures_klines(symbol=symbol, interval=client.KLINE_INTERVAL_15MINUTE, limit=100)
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
    df = pd.DataFrame(klines, columns=cols)
    df = df.drop(columns=['CloseTime', 'QuoteVolume', 'NumberTrades', 'TakerBuyBaseVolume', 'TakerBuyQuoteVolume', 'Ignore'])
    df[num_cols] = df[num_cols].apply(pd.to_numeric, errors='coerce')

    dates = []
    for date in df['Date']:
        dates.append(microTime(date))

    df = {
        'Open': list(df['Open']),
        'High': list(df['High']),
        'Low': list(df['Low']),
        'Close': list(df['Close']),
        'Date': dates
    }

    df_json = pd.read_json(json.dumps(df))
    df_json.to_excel(symbol + "_15MIN.xlsx")
