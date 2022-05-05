from binance.client import Client
import pandas as pd

client = Client("l8FqzEGOW91yP139vjZKDMs6oZJse4Isl3emol6dAMwVwKhHvOwH5irOVBvBhsVc", "eMlTWnJKQypSF2nlpCoWqTv6zyXej2hjDt2e7iqTNQbMoRQW3mOp94bkowj1OAtg", {"timeout": 40})


# =============================================================================
# Function of Exponential Moving Avarage
# =============================================================================
def ema(data, num):
    """
    Parameters
    ----------
    data : Data for calculate Ema
    num : Number of Ema's period
    Returns
    -------
    ema : Exponential moving avarage
    """
    ema = 0
    k = 2 / (num + 1)
    if ema == 0:
        first_ema = sum(data[-num: -1]) / (num - 1)
        ema = data[-1] * k + first_ema * (1 - k)
    else:
        ema = data[-1] * k + ema * (1 - k)
    return ema


# =============================================================================
# Function of MACD signal
# =============================================================================
def MACD(data):
    """
    Parameters
    ----------
    data : Data for calculate Macd

    Returns
    -------
    macdIndicator : signal of Macd
    """
    closeVal = pd.DataFrame(data)
    ema12 = closeVal.ewm(span=12).mean()
    ema26 = closeVal.ewm(span=26).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9).mean()
    macd = macd.values.tolist()
    signal = signal.values.tolist()
    if macd[-1] > signal[-1] and macd[-2] < signal[-2]:
        macdIndicator = 'BUY'
    elif macd[-1] < signal[-1] and macd[-2] > signal[-2]:
        macdIndicator = 'SELL'
    else:
        macdIndicator = 'HOLD'
    return macdIndicator


print(MACD(client.get_klines(symbol="BTCUSDT", interval=Client.KLINE_INTERVAL_30MINUTE)))
