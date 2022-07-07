import talib as ta
import numpy as np


def generateTillsonT3(historyMap, volume_factor, t3Length):
    close_array = historyMap["close"]
    high_array = historyMap["high"]
    low_array = historyMap["low"]
    ema_first_input = (high_array + low_array + 2 * close_array) / 4
    e1 = ta.EMA(ema_first_input, t3Length)
    e2 = ta.EMA(e1, t3Length)
    e3 = ta.EMA(e2, t3Length)
    e4 = ta.EMA(e3, t3Length)
    e5 = ta.EMA(e4, t3Length)
    e6 = ta.EMA(e5, t3Length)

    c1 = -1 * volume_factor * volume_factor * volume_factor
    c2 = 3 * volume_factor * volume_factor + 3 * volume_factor * volume_factor * volume_factor
    c3 = -6 * volume_factor * volume_factor - 3 * volume_factor - 3 * volume_factor * volume_factor * volume_factor
    c4 = 1 + 3 * volume_factor + volume_factor * volume_factor * volume_factor + 3 * volume_factor * volume_factor
    T3 = c1 * e6 + c2 * e5 + c3 * e4 + c4 * e3
    return T3


def getCoinHistory(klines):
    high = [float(entry[2]) for entry in klines]
    low = [float(entry[3]) for entry in klines]
    close = [float(entry[4]) for entry in klines]
    close_array = np.asarray(close)
    high_array = np.asarray(high)
    low_array = np.asarray(low)
    klinesMap = {
        "close": close_array,
        "high": high_array,
        "low": low_array
    }
    return klinesMap


def getSignal(klines, valueFactor, t3length, lastOperation):
    historyMap = getCoinHistory(klines)
    tillsont3 = generateTillsonT3(historyMap, valueFactor, t3length)
    t3_last = tillsont3[-1]
    t3_previous = tillsont3[-2]
    t3_prev_previous = tillsont3[-3]
    status = "HOLD"
    if t3_last > t3_previous and lastOperation != 'BUY':
        status = "BUY"
    elif t3_last < t3_previous and lastOperation != 'SELL':
        status = "SELL"
    return status
