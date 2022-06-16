import json

from binance.client import Client
import pandas as pd

symbol = "BNBUSDT"

client = Client()
klines = client.futures_klines(symbol=symbol, interval=client.KLINE_INTERVAL_15MINUTE, limit=300)
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
df = pd.DataFrame(klines, columns=cols)
df = df.drop(columns=['CloseTime', 'QuoteVolume', 'NumberTrades', 'TakerBuyBaseVolume', 'TakerBuyQuoteVolume', 'Ignore'])
df[num_cols] = df[num_cols].apply(pd.to_numeric, errors='coerce')

df = {
    'Open': list(df['Open']),
    'High': list(df['High']),
    'Low': list(df['Low']),
    'Close': list(df['Close']),
    'Date': list(df['Date'])
}

df_json = pd.read_json(json.dumps(df))
df_json.to_excel(symbol + "_15MIN.xlsx")
