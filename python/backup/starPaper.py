import termtables as tt
import pandas as pd

from binance.client import Client


def terminalTable(data):
    if len(data) > 0:
        header = list(data[0].keys())
        resultData = []
        for d in data:
            resultData.append(list(d.values()))
        tt.print(
            list(resultData),
            header=header,
        )


def topControl(klines):
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
    beforeClose = 0
    closeSIDE = None
    closeStar = 1
    lows = list(df['Low'])
    highs = list(df['High'])
    opens = list(df['Open'])
    volumes = list(df['Volume'])
    closeCount = 0
    closes = list(df['Close'])
    starsList = []
    reverse = 0
    for close in closes:
        if beforeClose > close:
            if closeSIDE == 'SHORT' or closeSIDE is None:
                if reverse != 1:
                    reverse = 0
                    if opens[closeCount] == highs[closeCount]:
                        if volumes[closeCount - 1] < volumes[closeCount] and closeSIDE is not None:
                            closeStar += 2
                        else:
                            closeStar += 1.5
                    else:
                        if volumes[closeCount - 1] < volumes[closeCount]:
                            closeStar += 1
                        else:
                            closeStar += 0.5
            else:
                if reverse >= 1:
                    print("sıfırlandı.")
                    reverse = 0
                    starsList.append(closeStar)
                    closeStar = 1
                else:
                    print("şans verildi. SHORT")
                    reverse += 1

            if reverse == 0:
                closeSIDE = 'SHORT'
        elif beforeClose < close:
            if closeSIDE == 'LONG' or closeSIDE is None:
                if reverse != 1:
                    reverse = 0
                    if opens[closeCount] == lows[closeCount]:
                        if volumes[closeCount - 1] < volumes[closeCount] and closeSIDE is not None:
                            closeStar += 2
                        else:
                            closeStar += 1.5
                    else:
                        if volumes[closeCount - 1] < volumes[closeCount]:
                            closeStar += 1
                        else:
                            closeStar += 0.5
            else:
                if reverse >= 1:
                    print("sıfırlandı.")
                    reverse = 0
                    starsList.append(closeStar)
                    closeStar = 1
                else:
                    print("şans verildi. LONG")
                    reverse += 1
            if reverse == 0:
                closeSIDE = 'LONG'
        beforeClose = close
        closeCount += 1
    return {'star': closeStar, 'side': closeSIDE, 'avarage': round(sum(starsList) / len(starsList), 2)}


client = Client()

# while True:
stars = {}
for item in client.futures_exchange_info()['symbols']:
    if 'USDT' in item['pair']:
        try:
            klines = client.futures_klines(symbol=item['pair'], interval=client.KLINE_INTERVAL_30MINUTE, limit=30)
            star = topControl(klines)
            if star['avarage'] not in stars:
                stars[star['avarage']] = []
            stars[star['avarage']].append({
                'paper': item['pair'],
                'star': star['star'],
                'side': star['side'],
                'avarage': star['avarage'],
            })
            print(item['pair'])
        except Exception as exception:
            print(str(exception))
            # terminalTable(stars[star['star']])
# print(stars[max(stars.keys())])

sortStars = list(stars.keys())
sortStars.sort()

for attr in sortStars:
    print(attr)
    print(terminalTable(stars[attr]))
