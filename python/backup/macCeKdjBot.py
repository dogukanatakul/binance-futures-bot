import time, sys, os, requests, uuid, talib, numpy
from datetime import datetime
from binance.client import Client
import pandas as pd
import termtables as tt
from helper import config
import talib as ta
from inspect import currentframe, getframeinfo

url = config('API', 'SITE')


def kdj(kline, N=9, M=2):
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
    low_list = df['Low'].rolling(window=N).min()
    low_list.fillna(value=df['Low'].expanding(min_periods=1).min(), inplace=True)
    high_list = df['High'].rolling(window=N).max()
    high_list.fillna(value=df['High'].expanding(min_periods=1).max(), inplace=True)
    rvs = (df['Close'] - low_list) / (high_list - low_list) * 100
    df['K'] = rvs.ewm(com=M, min_periods=0, adjust=True, ignore_na=False).mean()
    df['D'] = df['K'].ewm(com=M, min_periods=0, adjust=True, ignore_na=False).mean()
    df['J'] = 3 * df['K'] - 2 * df['D']
    return df.tail(1)['K'].item(), df.tail(1)['D'].item(), df.tail(1)['J'].item(), df['Date'][0]


def get_kdj(klines, period=9, signal=2):
    try:
        k, d, j, date = kdj(klines, period, signal)
        if float(j) > float(d) and float(d) < float(k):
            return {
                'K': k,
                'D': d,
                'J': j,
                'date': date,
                'type': 'LONG',
                'side': 'BUY'
            }
        else:
            return {
                'K': k,
                'D': d,
                'J': j,
                'date': date,
                'type': 'SHORT',
                'side': 'SELL'
            }
    except Exception as e:
        return False


def ce(kline, atr_period=22, atr_multiplier=3, lastCE=None):
    df = pd.DataFrame(kline)
    df.columns = ['Datetime',
                  'Open', 'High', 'Low', 'Close', 'volume',
                  'close_time', 'qav', 'num_trades',
                  'taker_base_vol', 'taker_quote_vol', 'ignore']
    df.index = [datetime.fromtimestamp(x / 1000.0) for x in df.close_time]

    df.drop(['close_time', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol', 'ignore'], axis=1, inplace=True)

    df['Open'] = pd.to_numeric(df["Open"], downcast="float")
    df["High"] = pd.to_numeric(df["High"], downcast="float")
    df["Low"] = pd.to_numeric(df["Low"], downcast="float")
    df["Close"] = pd.to_numeric(df["Close"], downcast="float")
    df["volume"] = pd.to_numeric(df["volume"], downcast="float")

    atr = ta.ATR(df['High'], df['Low'], df['Close'], timeperiod=atr_period)
    atr = list(filter(lambda v: v == v, atr))
    atr = round(atr_multiplier * atr[-1], 1)

    close = df['Close']
    close = list(filter(lambda v: v == v, close))

    low = df['Close'].rolling(window=atr_period).min()
    low.fillna(value=df['Close'].expanding(min_periods=atr_period).min(), inplace=True)
    low = list(filter(lambda v: v == v, low))

    high = df['Close'].rolling(window=atr_period).max()
    high.fillna(value=df['Close'].expanding(min_periods=atr_period).max(), inplace=True)
    high = list(filter(lambda v: v == v, high))

    longStopPrev = round(round(high[-2], 1) - atr, 1)
    # longStop = max(longStop, longStopPrev) if close[1] > longStopPrev else longStop

    shortStopPrev = round(round(low[-2], 1) + atr, 1)
    # shortStop = min(shortStop, shortStopPrev) if close[1] < shortStopPrev else shortStop

    # close1 = round(close[-2], 1)
    close = round(close[-1], 1)
    if close > shortStopPrev:
        dir = 'LONG'
    elif longStopPrev > close:
        dir = "SHORT"
    else:
        dir = lastCE
    return dir


def mac_dema(kline, dema_short=12, dema_long=26, dema_signal=9, lastMAC=None):
    df = pd.DataFrame(kline)
    df.columns = ['Datetime',
                  'Open', 'High', 'Low', 'Close', 'volume',
                  'close_time', 'qav', 'num_trades',
                  'taker_base_vol', 'taker_quote_vol', 'ignore']
    df.index = [datetime.fromtimestamp(x / 1000.0) for x in df.close_time]
    df.drop(['close_time', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol', 'ignore'], axis=1, inplace=True)
    df["Close"] = pd.to_numeric(df["Close"], downcast="float")
    close = df['Close']
    close = list(filter(lambda v: v == v, close))
    MMEslowa = talib.EMA(numpy.asarray(close), timeperiod=dema_long)
    MMEslowb = talib.EMA(MMEslowa, timeperiod=dema_long)
    DEMAslow = ((2 * MMEslowa) - MMEslowb)

    MMEfasta = talib.EMA(numpy.asarray(close), timeperiod=dema_short)
    MMEfastb = talib.EMA(MMEfasta, timeperiod=dema_short)
    DEMAfast = ((2 * MMEfasta) - MMEfastb)

    LigneMACD = DEMAfast - DEMAslow

    MMEsignala = talib.EMA(LigneMACD, timeperiod=dema_signal)
    MMEsignalb = talib.EMA(MMEsignala, timeperiod=dema_signal)
    Lignesignal = ((2 * MMEsignala) - MMEsignalb)

    if LigneMACD[-2] <= Lignesignal[-2] and LigneMACD[-1] >= Lignesignal[-1]:
        dir = 'LONG'
    elif LigneMACD[-2] >= Lignesignal[-2] and LigneMACD[-1] <= Lignesignal[-1]:
        dir = 'SHORT'
    else:
        dir = lastMAC
    return dir


def getOrderBalance(client, currenty, percent):
    minAmount = 1
    maxAmount = 134
    try:
        balance = client.futures_account_balance(asset=currenty)
        balance = next(x for x in balance if x["asset"] == currenty)
        percentBalance = float((float(balance['balance']) / 100) * percent)
        if percentBalance > maxAmount:
            percentBalance = maxAmount
        elif percentBalance < minAmount:
            percentBalance = minAmount
        return float(percentBalance)
    except:
        return False


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


def getPosition(client, symbol, side):
    infos = client.futures_position_information(symbol=symbol)
    positions = {}
    for info in infos:
        positions[info['positionSide']] = {
            'amount': abs(float(info['positionAmt'])),
            'entryPrice': float(info['entryPrice']),
            'markPrice': float(info['markPrice']),
            'profit': float(info['unRealizedProfit']),
            'fee': round(((abs(float(info['positionAmt'])) * 15) / 1000) * 0.0400, 2)
        }
    return positions[side]


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


def topControl(klines, diff, diff_max):
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
    side = None
    close = df['Close']
    close = list(filter(lambda v: v == v, close))
    if diff <= get_diff(close[-2], close[-1]) <= diff_max:
        side = 'LONG'
    elif diff <= get_diff(close[-1], close[-2]) <= diff_max:
        side = 'SHORT'
    return side


getBot = {
    'status': 0
}
version = None
while True:
    botUuid = "X"  # str(uuid.uuid4())
    while getBot['status'] == 0 or getBot['status'] == 2:
        time.sleep(0.5)
        getBot = requests.post(url + 'get-order/' + botUuid, headers={
            'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
        }).json()
        if version is not None and getBot['status'] == 0 and getBot['version'] != version:
            os.execl(sys.executable, sys.executable, *sys.argv)
        else:
            version = getBot['version']
    client = {}
    clientConnect = True
    clientConnectCount = 0
    while clientConnect:
        try:
            client = Client(str(getBot['api_key']), str(getBot['api_secret']), {"timeout": 300, 'proxies': getBot['proxy']})
            clientConnect = False
        except Exception as e:
            print(str(e))
            clientConnectCount += 1
            if ("Max retries exceeded" in str(e) or "Too many requests" in str(e) or "recvWindow" in str(e) or "Connection broken" in str(e)) and clientConnectCount < 3:
                time.sleep(0.5)
            elif "Way too many requests" in str(e) or "Read timed out." in str(e) or clientConnectCount >= 3:
                proxyOrder = requests.post(url + 'proxy-order/' + str(getBot['bot']), headers={
                    'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                }).json()
                getBot['proxy'] = proxyOrder['proxy']
            else:
                raise Exception(e)

    dual = client.futures_get_position_mode()
    if not dual['dualSidePosition']:
        client.futures_change_position_mode(dualSidePosition=True)
    result = client.futures_change_leverage(symbol=getBot['parity'], leverage=getBot['leverage'])
    info = client.futures_exchange_info()
    fractions = {}
    for item in info['symbols']:
        fractions[item['symbol']] = item['quantityPrecision']
    # LONG: BUY | SHORT: SELL
    sameTest = {
        'K': 0,
        'D': 0,
        'J': 0
    }
    operationLoop = True
    lastPrice = 0
    lastSide = 'HOLD'
    lastType = None
    lastCE = None
    last3MinCE = None
    lastMAC = None
    lastQuantity = None
    profitTrigger = False
    klines = {}
    klines30 = {}
    klines15 = {}
    klines3 = {}
    newTriggerOrder = False
    balance = 0

    # profit trigger
    profits = []
    profitDiff = []
    profitDiffAverage = int(config('SETTING', 'PROFIT_DIFF_MAX'))
    maxProfit = 0
    beforeProfit = None
    profitTurn = False
    profitTriggerKey = None
    maxDamage = 0
    maxDamageUSDT = 0
    orderStatus = False
    sideProfits = []
    maxTriggerCount = 0
    profitTriggerFee = False
    avarageLoss = 0
    last15Date = None
    # profit trigger END

    while operationLoop:
        try:
            minutes = {
                '1min': Client.KLINE_INTERVAL_1MINUTE,
                '5min': Client.KLINE_INTERVAL_5MINUTE,
                '15min': Client.KLINE_INTERVAL_15MINUTE,
                '30min': Client.KLINE_INTERVAL_30MINUTE,
                '1hour': Client.KLINE_INTERVAL_1HOUR,
                '4hour': Client.KLINE_INTERVAL_4HOUR
            }
            klineConnect = True
            klineConnectCount = 0
            while klineConnect:
                try:
                    klines = client.futures_klines(symbol=getBot['parity'], interval=minutes[str(getBot['time'])], limit=100)
                    klines30 = client.futures_klines(symbol=getBot['parity'], interval=Client.KLINE_INTERVAL_30MINUTE, limit=2)
                    klines15 = client.futures_klines(symbol=getBot['parity'], interval=Client.KLINE_INTERVAL_15MINUTE, limit=2)
                    klineConnect = False
                except Exception as e:
                    klineConnectCount += 1
                    if ("Max retries exceeded" in str(e) or "Too many requests" in str(e) or "recvWindow" in str(e) or "Connection broken" in str(e)) and klineConnectCount < 3:
                        time.sleep(0.5)
                    elif "Way too many requests" in str(e) or "Read timed out." in str(e) or klineConnectCount >= 3:
                        proxyOrder = requests.post(url + 'proxy-order/' + str(getBot['bot']), headers={
                            'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                        }).json()
                        client = Client(str(getBot['api_key']), str(getBot['api_secret']), {"timeout": 300, 'proxies': proxyOrder})
                    else:
                        raise Exception(e)
            getKDJ = get_kdj(klines, getBot['kdj_period'], getBot['kdj_signal'])
            if getKDJ['K'] != sameTest['K'] or getKDJ['D'] != sameTest['D'] or getKDJ['J'] != sameTest['J']:
                lastCE = ce(klines, getBot['atr_period'], getBot['atr_multiplier'], lastCE)
                lastMAC = mac_dema(klines, getBot['dema_short'], getBot['dema_long'], getBot['dema_signal'], lastMAC)
                last30 = topControl(klines30, float(config('SETTING', 'TRIGGER_30MIN')), float(config('SETTING', 'TRIGGER_30MIN_MAX')))
                last15 = topControl(klines15, float(config('SETTING', 'TRIGGER_15MIN')), float(config('SETTING', 'TRIGGER_15MIN_MAX')))
                topVerify = last30 == last15 and last30 == getKDJ['type']
                sameTest = {
                    'K': getKDJ['K'],
                    'D': getKDJ['D'],
                    'J': getKDJ['J']
                }
                # SYNC BOT
                syncBotWhile = True
                syncBotCount = 0
                while syncBotWhile:
                    syncBot = requests.post(url + 'get-order/' + str(getBot['bot']), headers={
                        'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                    })
                    if syncBot.status_code == 200:
                        for bt in syncBot.json().keys():
                            getBot[bt] = syncBot.json()[bt]
                        syncBotWhile = False
                    elif syncBotCount > 1:
                        raise Exception('server_error')
                    else:
                        syncBotCount += 1
                # SYNC BOT END

                if lastSide == 'HOLD' and getBot['status'] == 2 and lastPrice == 0:
                    setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                        'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                    }, json={
                        'line': getframeinfo(currentframe()).lineno,
                        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'TRIGGER_15_MIN': last15,
                        'TRIGGER_30_MIN': last30,
                        'KDJ': getKDJ['type'],
                        'MACD_DEMA': lastMAC,
                        'CE': lastCE,
                        'action': 'STOP',
                    }).status_code
                    if setBot != 200:
                        raise Exception('set_bot_fail')
                    raise Exception('STOP')
                else:
                    if getBot['status'] == 2 and orderStatus == False:
                        operationLoop = False
                        setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                            'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                        }, json={
                            'line': getframeinfo(currentframe()).lineno,
                            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'KDJ': getKDJ['type'],
                            'MACD_DEMA': lastMAC,
                            'CE': lastCE,
                            'side': lastSide,
                            'action': 'CLOSE',
                        }).status_code
                        if setBot != 200:
                            raise Exception('close')
                    else:
                        # Trigger after new same side order
                        if orderStatus == False and topVerify == True and last15Date is not None and last15Date != last15[0][0]:
                            checkSide = topControl(klines, float(config('SETTING', 'NEW_TRIGGER')), 10)
                            if checkSide == lastType:
                                newTriggerOrder = True
                        else:
                            newTriggerOrder = False
                        # END
                        if (lastSide != getKDJ['side'] and topVerify == True) or newTriggerOrder:
                            lastPrice = float(client.futures_ticker(symbol=getBot['parity'])['lastPrice'])
                            if lastSide != 'HOLD' and profitTrigger == False and orderStatus == True:
                                positionConnect = True
                                positionConnectCount = 0
                                try:
                                    position = getPosition(client, getBot['parity'], lastType)
                                    positionConnect = False
                                except Exception as e:
                                    positionConnectCount += 1
                                    if ("Max retries exceeded" in str(e) or "Too many requests" in str(e) or "recvWindow" in str(e) or "Connection broken" in str(e)) and positionConnectCount < 3:
                                        time.sleep(0.5)
                                    elif "Way too many requests" in str(e) or "Read timed out." in str(e) or positionConnectCount >= 3:
                                        proxyOrder = requests.post(url + 'proxy-order/' + str(getBot['bot']), headers={
                                            'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                                        }).json()
                                        client = Client(str(getBot['api_key']), str(getBot['api_secret']), {"timeout": 40, 'proxies': proxyOrder})
                                    else:
                                        raise Exception(e)

                                if position['amount'] > 0:
                                    # Binance
                                    orderStatus = False
                                    last15Date = klines15[0][0]
                                    client.futures_create_order(symbol=getBot['parity'], side=getKDJ['side'], positionSide=lastType, type="MARKET", quantity=lastQuantity)
                                    # Binance END
                                    setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                                        'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                                    }, json={
                                        'line': getframeinfo(currentframe()).lineno,
                                        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        'KDJ': getKDJ['type'],
                                        'MACD_DEMA': lastMAC,
                                        'CE': lastCE,
                                        'side': lastSide,
                                        'price': position['markPrice'],
                                        'profit': position['profit'],
                                        'quantity': position['amount'],
                                        'action': 'CLOSE',
                                    }).status_code
                                    if setBot != 200:
                                        raise Exception('set_bot_fail')
                                else:
                                    setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                                        'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                                    }, json={
                                        'line': getframeinfo(currentframe()).lineno,
                                        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        'TRIGGER_15_MIN': last15,
                                        'TRIGGER_30_MIN': last30,
                                        'KDJ': getKDJ['type'],
                                        'MACD_DEMA': lastMAC,
                                        'CE': lastCE,
                                        'side': lastSide,
                                        'action': 'MANUAL_STOP',
                                    }).status_code
                                    raise Exception('manual_stop')
                            else:
                                profitTrigger = False

                            if getBot['status'] == 2:
                                operationLoop = False
                                setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                                    'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                                }, json={
                                    'line': getframeinfo(currentframe()).lineno,
                                    'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    'KDJ': getKDJ['type'],
                                    'MACD_DEMA': lastMAC,
                                    'CE': lastCE,
                                    'side': lastSide,
                                    'action': 'CLOSE',
                                }).status_code
                                if setBot != 200:
                                    raise Exception('close')
                            else:
                                lastSide = getKDJ['side']
                                lastType = getKDJ['type']

                                # profit trigger
                                profits = []
                                profitDiff = []
                                profitDiffAverage = int(config('SETTING', 'PROFIT_DIFF_MAX'))
                                maxProfit = 0
                                beforeProfit = None
                                profitTurn = False
                                profitTriggerKey = None
                                maxDamage = 0
                                sideProfits = []
                                maxTriggerCount = 0
                                profitTriggerFee = False
                                avarageLoss = 0
                                last15Date = None
                                # profit trigger END

                                # Binance
                                balance = getOrderBalance(client, "USDT", int(getBot['percent']))

                                # profit trigger
                                maxDamageUSDT = round((balance / 100) * float(config('SETTING', 'MAX_DAMAGE_USDT_PERCENT')), 2)
                                # profit trigger END

                                lastQuantity = "{:0.0{}f}".format(float((balance / lastPrice) * getBot['leverage']), fractions[getBot['parity']])
                                if float(lastQuantity) <= 0:
                                    raise Exception("Bakiye hatası")
                                client.futures_create_order(symbol=getBot['parity'], side=lastSide, type='MARKET', quantity=lastQuantity, positionSide=lastType)
                                # Binance END
                                orderStatus = True

                                setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                                    'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                                }, json={
                                    'line': getframeinfo(currentframe()).lineno,
                                    'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    'TRIGGER_15_MIN': last15,
                                    'TRIGGER_30_MIN': last30,
                                    'KDJ': getKDJ['type'],
                                    'MACD_DEMA': lastMAC,
                                    'CE': lastCE,
                                    'side': lastSide,
                                    'position': lastType,
                                    'balance': balance,
                                    'quantity': lastQuantity,
                                    'price': lastPrice,
                                    'action': 'OPEN',
                                }).status_code
                                if setBot != 200:
                                    raise Exception('set_bot_fail')
                        else:
                            if not orderStatus:
                                setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                                    'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                                }, json={
                                    'line': getframeinfo(currentframe()).lineno,
                                    'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    'TRIGGER_15_MIN': last15,
                                    'TRIGGER_30_MIN': last30,
                                    'KDJ': getKDJ['type'],
                                    'MACD_DEMA': lastMAC,
                                    'CE': lastCE,
                                    'action': 'ORDER_START_WAITING',
                                }).status_code
                                if setBot != 200:
                                    raise Exception('set_bot_fail')
                            elif lastPrice != 0 and profitTrigger == False and orderStatus == True:
                                # get Position
                                positionConnect = True
                                positionConnectCount = 0
                                try:
                                    position = getPosition(client, getBot['parity'], lastType)
                                    positionConnect = False
                                except Exception as e:
                                    positionConnectCount += 1
                                    if ("Max retries exceeded" in str(e) or "Too many requests" in str(e) or "recvWindow" in str(e) or "Connection broken" in str(e)) and positionConnectCount < 3:
                                        time.sleep(0.5)
                                    elif "Way too many requests" in str(e) or "Read timed out." in str(e) or positionConnectCount >= 3:
                                        proxyOrder = requests.post(url + 'proxy-order/' + str(getBot['bot']), headers={
                                            'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                                        }).json()
                                        client = Client(str(getBot['api_key']), str(getBot['api_secret']), {"timeout": 40, 'proxies': proxyOrder})
                                    else:
                                        raise Exception(e)

                                profit = round(position['profit'], 2)
                                if profit != beforeProfit:
                                    print(profit, "profit")
                                    if profit > 0:
                                        maxDamage = 0
                                        avarageLoss = 0

                                        if profit >= (position['fee'] * float(config('SETTING', 'FEE_LEVERAGE'))):
                                            profitTriggerFee = True
                                        if profit not in sideProfits:
                                            sideProfits.append(profit)
                                        maxDamage = 0
                                        if profit > maxProfit:
                                            maxProfit = profit
                                            maxTriggerCount = 0
                                        elif abs(get_diff(profit, maxProfit)) > profitDiffAverage and len(sideProfits) >= int(config('SETTING', 'MIN_PROFIT')) and profitTriggerFee == True:
                                            print(maxTriggerCount, "maxTriggerCount")
                                            maxTriggerCount += 1
                                            if maxTriggerCount >= int(config('SETTING', 'MAX_TRIGGER_COUNT')):
                                                profitTurn = True
                                                profitTriggerKey = "MaxTrigger"
                                    elif profit <= 0:
                                        profits = []
                                        profitDiff = []
                                        profitDiffAverage = int(config('SETTING', 'PROFIT_DIFF_MAX'))
                                        maxProfit = 0
                                        sideProfits = []
                                        maxTriggerCount = 0
                                        profitTriggerFee = False
                                        if avarageLoss < abs(profit):
                                            maxDamage += 1
                                            print(maxDamage, "maxDamage")
                                            avarageLoss = abs(profit)

                                        if maxDamage >= int(config('SETTING', 'MAX_DAMAGE')):
                                            profitTurn = True
                                            profitTriggerKey = "DamageTrigger"

                                    if beforeProfit is not None:
                                        diffCurrent = round(abs(get_diff(profit, beforeProfit)), 2)
                                        if diffCurrent not in profitDiff:
                                            profitDiff.append(diffCurrent)
                                            profitDiffAverage = (abs(round(sum(profitDiff) / len(profitDiff), 2)) / 100)
                                            if profitDiffAverage > int(config('SETTING', 'PROFIT_DIFF_MAX')):
                                                profitDiffAverage = int(config('SETTING', 'PROFIT_DIFF_MAX'))
                                            elif profitDiffAverage < int(config('SETTING', 'PROFIT_DIFF_MIN')):
                                                profitDiffAverage = int(config('SETTING', 'PROFIT_DIFF_MIN'))

                                            profitDiffAverage = profitDiffAverage - int(10 - (get_diff(maxProfit, ((balance / 100) * 15)) / 10))
                                            print(profitDiffAverage, "profitDiffAverage")
                                    beforeProfit = profit

                                if profitTurn:
                                    profitTrigger = True
                                    orderStatus = False
                                    last15Date = klines15[0][0]
                                    client.futures_create_order(symbol=getBot['parity'], side='SELL' if lastType == 'LONG' else "BUY", positionSide=lastType, type="MARKET", quantity=lastQuantity)
                                    setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                                        'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                                    }, json={
                                        'line': getframeinfo(currentframe()).lineno,
                                        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        'TRIGGER_15_MIN': last15,
                                        'TRIGGER_30_MIN': last30,
                                        'KDJ': getKDJ['type'],
                                        'MACD_DEMA': lastMAC,
                                        'CE': lastCE,
                                        'side': lastSide,
                                        'price': position['markPrice'],
                                        'profit': position['profit'],
                                        'quantity': position['amount'],
                                        'action': profitTriggerKey,
                                    }).status_code
                                    if setBot != 200:
                                        raise Exception('set_bot_fail')

                                    # get Position END

                # Max Request Sleep
                time.sleep(0.5)
                # Max Request Sleep
            else:
                time.sleep(0.5)
        except Exception as exception:
            operationLoop = False
            getBot['status'] = 2
            print("emir kapatıldı!!")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            setBot = requests.post(url + 'set-error', headers={
                'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
            }, json={
                'bot': getBot['bot'],
                'errors': [
                    str(exc_type),
                    str(fname),
                    str(exc_tb.tb_lineno),
                    str(exception)
                ]
            }).status_code
            if getBot['version'] != version:
                print("yeniden başlatma")
                os.execl(sys.executable, sys.executable, *sys.argv)
