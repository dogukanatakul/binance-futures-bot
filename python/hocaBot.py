import time, sys, os, requests, uuid, talib, numpy
from datetime import datetime
from binance.client import Client
import pandas as pd
import termtables as tt
from helper import config
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
        if float(j) > float(d):
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
    botUuid = str(uuid.uuid4())
    while getBot['status'] == 0 or getBot['status'] == 2:
        time.sleep(0.5)
        getBot = requests.post(url + 'get-order/' + botUuid, headers={
            'neresi': 'dogunun+billurlari'
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
                    'neresi': 'dogunun+billurlari'
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
    orderStatus = False
    profitTurn = False
    profitTriggerKey = None

    firstTypeTrigger = 0
    fakeTrigger = 0
    fakeTriggerSide = 0
    maxDamageUSDT = 0
    maxDamageCount = 0
    maxDamageBefore = 0

    lastCE = None
    lastMAC = None
    lastQuantity = None
    profitTrigger = False
    klines = {}
    newTriggerOrder = False
    balance = 0
    reverseType = {
        'LONG': 'SHORT',
        'SHORT': 'LONG'
    }

    while operationLoop:
        try:
            klineConnect = True
            klineConnectCount = 0
            while klineConnect:
                try:
                    klines = client.futures_klines(symbol=getBot['parity'], interval=client.KLINE_INTERVAL_5MINUTE, limit=300)
                    klineConnect = False
                except Exception as e:
                    klineConnectCount += 1
                    if ("Max retries exceeded" in str(e) or "Too many requests" in str(e) or "recvWindow" in str(e) or "Connection broken" in str(e)) and klineConnectCount < 3:
                        time.sleep(0.5)
                    elif "Way too many requests" in str(e) or "Read timed out." in str(e) or klineConnectCount >= 3:
                        proxyOrder = requests.post(url + 'proxy-order/' + str(getBot['bot']), headers={
                            'neresi': 'dogunun+billurlari'
                        }).json()
                        client = Client(str(getBot['api_key']), str(getBot['api_secret']), {"timeout": 300, 'proxies': proxyOrder})
                    else:
                        raise Exception(e)
            getKDJ = get_kdj(klines, getBot['kdj_period'], getBot['kdj_signal'])
            if getKDJ['K'] != sameTest['K'] or getKDJ['D'] != sameTest['D'] or getKDJ['J'] != sameTest['J']:
                # first side check
                if firstTypeTrigger <= int(config('SETTING', 'FIRST_FAKE')):
                    if lastSide == getKDJ['side']:
                        firstTypeTrigger += 1
                    else:
                        firstTypeTrigger = 0
                    # first side check END
                    lastSide = getKDJ['side']

                if fakeTriggerSide == getKDJ['side'] and firstTypeTrigger >= int(config('SETTING', 'FIRST_FAKE')):
                    fakeTrigger += 1
                else:
                    fakeTrigger = 0
                fakeTriggerSide = getKDJ['side']

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
                        'neresi': 'dogunun+billurlari'
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
                        'neresi': 'dogunun+billurlari'
                    }, json={
                        'line': getframeinfo(currentframe()).lineno,
                        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
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
                            'neresi': 'dogunun+billurlari'
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
                        # START ORDER
                        if lastSide != getKDJ['side'] and firstTypeTrigger >= int(config('SETTING', 'FIRST_FAKE')) and fakeTrigger >= int(config('SETTING', 'FAKE_TRIGGER')) and orderStatus == False:
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
                                            'neresi': 'dogunun+billurlari'
                                        }).json()
                                        client = Client(str(getBot['api_key']), str(getBot['api_secret']), {"timeout": 40, 'proxies': proxyOrder})
                                    else:
                                        raise Exception(e)

                                if position['amount'] > 0:
                                    # Binance
                                    orderStatus = False
                                    client.futures_create_order(symbol=getBot['parity'], side=getKDJ['side'], positionSide=lastType, type="MARKET", quantity=lastQuantity)
                                    # Binance END
                                    setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                                        'neresi': 'dogunun+billurlari'
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
                                        'neresi': 'dogunun+billurlari'
                                    }, json={
                                        'line': getframeinfo(currentframe()).lineno,
                                        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

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
                                    'neresi': 'dogunun+billurlari'
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
                                lastMAC = None

                                # Binance
                                balance = getOrderBalance(client, "USDT", int(getBot['percent']))

                                # profit trigger
                                maxDamageUSDT = round((balance / 100) * float(config('SETTING', 'MAX_DAMAGE_USDT_PERCENT')), 2)
                                maxDamageCount = 0
                                maxDamageBefore = 0
                                # profit trigger END

                                lastQuantity = "{:0.0{}f}".format(float((balance / lastPrice) * getBot['leverage']), fractions[getBot['parity']])
                                if float(lastQuantity) <= 0:
                                    raise Exception("Bakiye hatası")
                                client.futures_create_order(symbol=getBot['parity'], side=lastSide, type='MARKET', quantity=lastQuantity, positionSide=lastType)
                                # Binance END
                                orderStatus = True

                                setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                                    'neresi': 'dogunun+billurlari'
                                }, json={
                                    'line': getframeinfo(currentframe()).lineno,
                                    'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
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
                                    'neresi': 'dogunun+billurlari'
                                }, json={
                                    'line': getframeinfo(currentframe()).lineno,
                                    'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    'KDJ': getKDJ['type'],
                                    'MACD_DEMA': lastMAC,
                                    'CE': lastCE,
                                    'action': 'ORDER_START_WAITING',
                                }).status_code
                                if setBot != 200:
                                    raise Exception('set_bot_fail')
                            elif lastPrice != 0 and profitTrigger == False and orderStatus == True:

                                macdConnect = True
                                macdConnectCount = 0
                                try:
                                    position = getPosition(client, getBot['parity'], lastType)
                                    klines = client.futures_klines(symbol=getBot['parity'], interval=client.KLINE_INTERVAL_3MINUTE, limit=300)
                                    # short / long
                                    lastMAC = mac_dema(klines, getBot['dema_short'], getBot['dema_long'], getBot['dema_signal'], lastMAC)
                                    macdConnect = False
                                except Exception as e:
                                    macdConnectCount += 1
                                    if ("Max retries exceeded" in str(e) or "Too many requests" in str(e) or "recvWindow" in str(e) or "Connection broken" in str(e)) and macdConnectCount < 3:
                                        time.sleep(0.5)
                                    elif "Way too many requests" in str(e) or "Read timed out." in str(e) or macdConnectCount >= 3:
                                        proxyOrder = requests.post(url + 'proxy-order/' + str(getBot['bot']), headers={
                                            'neresi': 'dogunun+billurlari'
                                        }).json()
                                        client = Client(str(getBot['api_key']), str(getBot['api_secret']), {"timeout": 40, 'proxies': proxyOrder})
                                    else:
                                        raise Exception(e)
                                if position['amount'] <= 0:
                                    raise Exception('close')
                                elif position['profit'] > 0:
                                    if position['profit'] >= balance:
                                        profitTriggerKey = "TRIGGER_PROFIT_100"
                                        profitTurn = True
                                    elif lastMAC is not None:
                                        profitTriggerKey = "TRIGGER_MACDDEMA"
                                        profitTurn = True
                                elif position['profit'] < 0:
                                    if lastMAC is not None:
                                        profitTriggerKey = "TRIGGER_MACDDEMA"
                                        profitTurn = True
                                    elif abs(position['profit']) >= maxDamageUSDT:
                                        if maxDamageBefore < abs(position['profit']):
                                            maxDamageCount += 1
                                            if maxDamageCount >= int(config('SETTING', 'MAX_DAMAGE_COUNT')):
                                                profitTriggerKey = "MAX_DAMAGE"
                                                profitTurn = True
                                        else:
                                            maxDamageCount = 0

                                        maxDamageBefore = abs(position['profit'])

                                if profitTurn:
                                    profitTrigger = True
                                    orderStatus = False
                                    client.futures_create_order(symbol=getBot['parity'], side='SELL' if lastType == 'LONG' else "BUY", positionSide=lastType, type="MARKET", quantity=lastQuantity)
                                    setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                                        'neresi': 'dogunun+billurlari'
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
                                        'action': profitTriggerKey,
                                    }).status_code
                                    if setBot != 200:
                                        raise Exception('set_bot_fail')

                                # emir bozma yeri

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
                'neresi': 'dogunun+billurlari'
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
