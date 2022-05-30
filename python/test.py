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


client = Client()
klines = client.futures_klines(symbol='XRPUSDT', interval=Client.KLINE_INTERVAL_6HOUR, limit=300)

def maxProfit(klines):
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
    high = list(df['High'])
    high.reverse()
    low = list(df['Low'])
    low.reverse()
    diffs = []
    for key in range(0, 3):
        diffs.append(get_diff(float(low[key]), float(high[key])))
    calc = int((sum(diffs) / len(diffs)) * 10)
    return calc if float(config('SETTING', 'MAX_PROFIT'))>calc else float(config('SETTING', 'MAX_PROFIT'))
