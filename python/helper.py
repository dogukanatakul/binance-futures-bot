import configparser
import os
import pandas as pd


def config(cat, param):
    cnf = configparser.ConfigParser()
    cnf.read(os.path.dirname(os.path.realpath(__file__)) + '/config.ini')
    return str(cnf.get(cat, param))


def ema(data, num):
    """
    https://github.com/Tousama/BinanceApiDataAnalysis/blob/557c2642da4a7eafc679c4c3b8b242d8a02cd5ab/binance.py
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


def MACD(data):
    """
    https://github.com/Tousama/BinanceApiDataAnalysis/blob/557c2642da4a7eafc679c4c3b8b242d8a02cd5ab/binance.py
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
