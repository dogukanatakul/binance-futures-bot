from binance.client import Client
import pandas as pd

client = Client()
klines = client.futures_klines(symbol="BNBUSDT", interval=Client.KLINE_INTERVAL_3MINUTE, limit=10)
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


print(klines)
