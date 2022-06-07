from binance.client import Client
import pandas as pd


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


def sideCalc(klines):
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
    if df['Close'][1] > df['Close'][0] and abs(get_diff(df['Low'][1], df['Close'][1])) > 1 and abs(get_diff(df['High'][1], df['Close'][1])) < 2:
        return 'SHORT'
    elif df['Close'][1] < df['Close'][0] and abs(get_diff(df['High'][1], df['Close'][1])) > 1 and abs(get_diff(df['Low'][1], df['Close'][1])) < 2:
        return 'LONG'
    else:
        return 'HOLD'


client = Client()
print(sideCalc(client.futures_klines(symbol='BNBUSDT', interval=Client.KLINE_INTERVAL_1DAY, limit=2)))
