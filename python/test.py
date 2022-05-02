from binance.client import Client
import pandas as pd

client = Client()

klines100 = client.get_klines(symbol="BTCUSDT", interval=client.KLINE_INTERVAL_1HOUR, limit=10)


def kdj(kline, period, signal):
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
    df = pd.DataFrame(kline, columns=cols)
    df = df.drop(columns=['CloseTime', 'QuoteVolume', 'NumberTrades', 'TakerBuyBaseVolume', 'TakerBuyQuoteVolume', 'Ignore'])
    df[num_cols] = df[num_cols].apply(pd.to_numeric, errors='coerce')
    low_list = df['Low'].rolling(period, min_periods=period).min()
    low_list.fillna(value=df['Low'].expanding().min(), inplace=True)
    high_list = df['High'].rolling(period, min_periods=period).max()
    high_list.fillna(value=df['High'].expanding().max(), inplace=True)
    rsv = (df['Close'] - low_list) / (high_list - low_list) * 100
    df_kdj = df.copy()
    df_kdj['K'] = pd.DataFrame(rsv).ewm(com=signal).mean()
    df_kdj['D'] = df_kdj['K'].ewm(com=signal).mean()
    df_kdj['J'] = 3 * df_kdj['K'] - 2 * df_kdj['D']
    return df_kdj.tail(1)['K'].item(), df_kdj.tail(1)['D'].item(), df_kdj.tail(1)['J'].item()


k, d, j = kdj(klines100, 5, 2)
print(k, d, j)
k, d, j = kdj(klines100, 9, 3)
print(k, d, j)
