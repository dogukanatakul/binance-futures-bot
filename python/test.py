import json, os, datetime, requests
import pandas as pd
from helper import config


def microTime(dt):
    return datetime.datetime.fromtimestamp(dt / 1000.0).strftime("%Y-%m-%d %H:%M:%S")


times = [
    1656186840000,
    1656187020000,
    1656187200000,
    1656187380000,
    1656187560000,
    1656187740000,
    1656187920000,
    1656188100000,
    1656188280000,
]
lastDate = 0
for tmm in times:
    klines = json.loads(open(os.path.dirname(os.path.realpath(__file__)) + '/datas/' + str(tmm) + '.json', "r").read())
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
    df_json.to_excel(os.path.dirname(os.path.realpath(__file__)) + "/" + microTime(tmm) + ".xlsx")
