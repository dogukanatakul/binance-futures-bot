import pandas as pd
from binance.client import Client


def brs(klines, M=0.00, T=0.00):
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
    BRS = (((list(df['Close'])[-1] - (sum(df['Low']) / len(df['Low']))) / ((sum(df['High']) / len(df['High'])) - (sum(df['Low']) / len(df['Low'])))) * 100) * 1
    M = 2.5 / 3 * M + 0.5 / 3 * BRS
    T = 2.5 / 3 * T + 0.5 / 3 * M
    C = 3 * M - 2 * T
    if M > C:
        result = {
            'type': 'LONG',
            'side': 'BUY',
            'BRS': BRS,
            'M': M,
            'T': T,
            'C': C,
        }
    else:
        result = {
            'type': 'SHORT',
            'side': 'SELL',
            'BRS': BRS,
            'M': M,
            'T': T,
            'C': C,
        }
    return result


client = Client()
klines = client.futures_klines(symbol="BNBUSDT", interval="15m", limit=11)
print(brs(klines, 10, 10))
