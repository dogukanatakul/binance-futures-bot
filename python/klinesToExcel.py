import json, os, datetime, requests
import time
import pandas as pd
from binance.client import Client
from helper import config


def microTime(dt):
    return datetime.datetime.fromtimestamp(dt / 1000.0).strftime("%Y-%m-%d %H:%M:%S")


while True:
    req = requests.post(config('API', 'SITE') + 'exports', headers={
        'neresi': 'dogunun+billurlari'
    }).json()
    if req['id'] != 0:
        try:
            client = Client()
            klines = client.futures_klines(symbol=req['parity'], interval=req['time'], limit=100)
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

            dfParse = {
                'Open': list(df['Open']),
                'High': list(df['High']),
                'Low': list(df['Low']),
                'Close': list(df['Close']),
                'Date': dates
            }
            df_json = pd.read_json(json.dumps(dfParse))
            df_json.to_excel(os.path.dirname(os.path.realpath(__file__)) + "/../storage/app/export/" + req['parity'] + "_" + req['time'] + ".xlsx")
            requests.post(config('API', 'SITE') + 'exports', headers={
                'neresi': 'dogunun+billurlari'
            }, json={
                'id': req['id']
            }).json()
        except:
            time.sleep(10)
