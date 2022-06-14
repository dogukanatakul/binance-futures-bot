import os, json
import pandas as pd
from helper import config
from binance.client import Client


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


def profitMax(klines, leverage):
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
    df = pd.DataFrame(klines, columns=cols)
    df = df.drop(columns=['CloseTime', 'QuoteVolume', 'NumberTrades', 'TakerBuyBaseVolume', 'TakerBuyQuoteVolume', 'Ignore'])
    high = list(df['High'])
    high.reverse()
    high.pop(0)
    low = list(df['Low'])
    low.reverse()
    low.pop(0)
    diffs = []
    for key in range(0, 10):
        diffs.append(get_diff(float(low[key]), float(high[key])))
    minDiff = int(min(diffs) * leverage)
    maxDiff = int(max(diffs) * leverage)
    averageDiff = int((sum(diffs) / len(diffs)) * leverage)
    return {
        'profit': {
            maxDiff: {
                'count': 1,
                'percent': 15,
            },
            averageDiff: {
                'count': 2,
                'percent': 20,
            },
            minDiff: {
                'count': 3,
                'percent': 40,
            },
        },
        'default': minDiff
    }


client = Client()
klines = client.futures_klines(symbol="BTCUSDT", interval=client.KLINE_INTERVAL_1HOUR, limit=300)

for attr, value in profitMax(klines, 10)['profit'].items():
    print(attr, value)
