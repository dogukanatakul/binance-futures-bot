import time, sys, os, requests, uuid, talib, numpy
from datetime import datetime
from binance.client import Client
import pandas as pd
import json
from helper import config
from inspect import currentframe, getframeinfo
import logging

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


def get_kdj(klines, period=9, signal=2, lastSide=None, multiplier: float = 1.1):
    try:
        k, d, j, date = kdj(klines, period, signal)
        if lastSide == 'BUY':
            d = d * multiplier
        elif lastSide == 'SELL':
            j = j * multiplier
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
            'fee': round(((abs(float(info['positionAmt'])) * 15) / 1000) * 0.0400, 2),
            'leverage': int(info['leverage'])
        }
    return positions[side]


def profitMax(klines):
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
    low = list(df['Low'])
    low.reverse()
    diffs = []
    for key in range(0, 5):
        diffs.append(get_diff(float(low[key]), float(high[key])))
    calc = int((sum(diffs) / len(diffs)) * 10)
    return calc if float(config('SETTING', 'MAX_PROFIT')) > calc else float(config('SETTING', 'MAX_PROFIT'))


def sideCalc(klines):
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
    if df['Close'][1] > df['Close'][0] and abs(get_diff(df['Low'][1], df['Close'][1])) > 1 and abs(get_diff(df['High'][1], df['Close'][1])) < 1.5:
        return 'BUY'
    elif df['Close'][1] < df['Close'][0] and abs(get_diff(df['High'][1], df['Close'][1])) > 1 and abs(get_diff(df['Low'][1], df['Close'][1])) < 1.5:
        return 'SELL'
    else:
        return 'HOLD'


def jsonData(bot, status='GET', data={}):
    if status == 'SET':
        with open(os.path.dirname(os.path.realpath(__file__)) + "/datas/" + bot + '.json', 'w') as outfile:
            outfile.write(json.dumps(data))
        return True
    elif status == 'DELETE':
        os.remove((os.path.dirname(os.path.realpath(__file__)) + "/datas/" + bot + '.json'))
    else:
        if os.path.exists(os.path.dirname(os.path.realpath(__file__)) + "/datas/" + bot + '.json'):
            return json.loads(open(os.path.dirname(os.path.realpath(__file__)) + "/datas/" + bot + '.json', "r").read())
        else:
            return False


getBot = {
    'status': 0
}
version = None
while True:
    botUuid = str(uuid.uuid4())
    while getBot['status'] == 0:
        time.sleep(float(config('SETTING', 'TIME_SLEEP')))
        getBot = requests.post(url + 'get-order/' + botUuid, headers={
            'neresi': 'dogunun+billurlari'
        }).json()
        if version is not None and getBot['status'] == 0 and getBot['version'] != version:
            os.execl(sys.executable, sys.executable, *sys.argv)
        else:
            version = getBot['version']
    logging.basicConfig(filename=os.path.dirname(os.path.realpath(__file__)) + "/datas/" + str(getBot['bot']) + '.log', level=logging.DEBUG)
    try:
        client = {}
        clientConnect = True
        clientConnectCount = 0
        while clientConnect:
            try:
                client = Client(str(getBot['api_key']), str(getBot['api_secret']), {"timeout": 300, 'proxies': getBot['proxy']})
                clientConnect = False
            except Exception as e:
                clientConnectCount += 1
                if ("Max retries exceeded" in str(e) or "Too many requests" in str(e) or "recvWindow" in str(e) or "Connection broken" in str(e)) and clientConnectCount < 3:
                    time.sleep(float(config('SETTING', 'TIME_SLEEP')))
                elif "Way too many requests" in str(e) or "Read timed out." in str(e) or (3 <= clientConnectCount <= 6):
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
        if getBot['transfer'] is not None:
            botElements = jsonData(getBot['transfer'], 'GET')
            if not botElements:
                errBotWhile = True
                errBotCount = 0
                while errBotWhile:
                    errBot = requests.post(url + 'set-error', headers={
                        'neresi': 'dogunun+billurlari'
                    }, json={
                        'bot': getBot['bot'],
                        'errors': [
                            "ilerleme dosyası bulunamadı.",
                        ]
                    })
                    if errBot.status_code == 200:
                        errBotWhile = False
                    elif errBotCount >= int(config('API', 'ERR_COUNT')):
                        raise Exception('server_error')
                    else:
                        time.sleep(1)
                        errBotCount += 1
                sys.exit(0)
            else:
                jsonData(getBot['bot'], 'SET', botElements)
                jsonData(getBot['transfer'], 'DELETE')
        else:
            klineConnect = True
            klineConnectCount = 0
            klines1DAY = {}
            while klineConnect:
                try:
                    klines1DAY = client.futures_klines(symbol=getBot['parity'], interval=Client.KLINE_INTERVAL_1DAY, limit=2)
                    klineConnect = False
                except Exception as e:
                    klineConnectCount += 1
                    if ("Max retries exceeded" in str(e) or "Too many requests" in str(e) or "recvWindow" in str(e) or "Connection broken" in str(e)) and klineConnectCount < 3:
                        time.sleep(float(config('SETTING', 'TIME_SLEEP')))
                    elif "Way too many requests" in str(e) or "Read timed out." in str(e) or (3 <= klineConnectCount <= 6):
                        proxyOrder = requests.post(url + 'proxy-order/' + str(getBot['bot']), headers={
                            'neresi': 'dogunun+billurlari'
                        }).json()
                        client = Client(str(getBot['api_key']), str(getBot['api_secret']), {"timeout": 300, 'proxies': proxyOrder})
                    else:
                        raise Exception(e)
            botElements = {
                'lastPrice': 0,
                'lastSide': 'HOLD',
                'guessSide': sideCalc(klines1DAY),
                'guessSideStatus': False,
                'guessSideRetry': 0,
                'lastType': None,
                'orderStatus': False,
                'profitTurn': False,
                'profitTriggerKey': None,
                'firstTypeTrigger': 0,
                'fakeTrigger': 0,
                'fakeTriggerSide': 0,
                'maxDamageUSDT': 0,
                'maxDamageCount': 0,
                'maxDamageBefore': 0,
                'maxProfit': 100,
                'maxProfitCount': 0,
                'maxProfitStatus': False,
                'maxProfitMax': 0,
                'maxProfitMin': 0,
                'lastCE': None,
                'lastMAC': None,
                'lastQuantity': None,
                'profitTrigger': False,
                'newTriggerOrder': False,
                'balance': 0,
                'setLeverage': True,
                'DEMATriggerStatus': False,
                'firstLogin': True
            }
            jsonData(getBot['bot'], 'SET', botElements)
        klines = {}
        reverseType = {
            'LONG': 'SHORT',
            'SHORT': 'LONG'
        }
        reverseSide = {
            'BUY': 'SELL',
            'SELL': 'BUY'
        }

        while operationLoop:
            try:
                klineConnect = True
                klineConnectCount = 0
                while klineConnect:
                    try:
                        klines = client.futures_klines(symbol=getBot['parity'], interval=client.KLINE_INTERVAL_1HOUR, limit=300)
                        klineConnect = False
                    except Exception as e:
                        klineConnectCount += 1
                        if ("Max retries exceeded" in str(e) or "Too many requests" in str(e) or "recvWindow" in str(e) or "Connection broken" in str(e)) and klineConnectCount < 3:
                            time.sleep(float(config('SETTING', 'TIME_SLEEP')))
                        elif "Way too many requests" in str(e) or "Read timed out." in str(e) or (3 <= klineConnectCount <= 6):
                            proxyOrder = requests.post(url + 'proxy-order/' + str(getBot['bot']), headers={
                                'neresi': 'dogunun+billurlari'
                            }).json()
                            client = Client(str(getBot['api_key']), str(getBot['api_secret']), {"timeout": 300, 'proxies': proxyOrder})
                        else:
                            raise Exception(e)
                getKDJ = get_kdj(klines, getBot['kdj_period'], getBot['kdj_signal'], botElements['lastSide'], float(config('SETTING', 'KDJ_X')))
                if getKDJ['K'] != sameTest['K'] or getKDJ['D'] != sameTest['D'] or getKDJ['J'] != sameTest['J']:

                    # first side check
                    if botElements['firstLogin']:
                        if botElements['guessSide'] == 'HOLD':
                            if botElements['firstTypeTrigger'] <= int(config('SETTING', 'FIRST_FAKE')):
                                if botElements['lastSide'] == getKDJ['side']:
                                    botElements['firstTypeTrigger'] += 1
                                else:
                                    botElements['firstTypeTrigger'] = 0
                                # first side check END
                                botElements['lastSide'] = getKDJ['side']

                            if botElements['fakeTriggerSide'] == getKDJ['side'] and botElements['firstTypeTrigger'] >= int(config('SETTING', 'FIRST_FAKE')):
                                botElements['fakeTrigger'] += 1
                            else:
                                botElements['fakeTrigger'] = 0
                            botElements['fakeTriggerSide'] = getKDJ['side']
                            jsonData(getBot['bot'], 'SET', botElements)
                        else:
                            if botElements['guessSide'] == getKDJ['side'] and abs(get_diff(getKDJ['D'], getKDJ['J'])) < 20 and botElements['guessSideStatus'] == True:
                                botElements['firstTypeTrigger'] = int(config('SETTING', 'FIRST_FAKE'))
                                botElements['fakeTrigger'] = int(config('SETTING', 'FAKE_TRIGGER'))
                            else:
                                if getKDJ['side'] == reverseSide[botElements['guessSide']]:
                                    botElements['firstTypeTrigger'] += 1
                                    if botElements['firstTypeTrigger'] >= int(config('SETTING', 'FIRST_FAKE')):
                                        botElements['guessSideStatus'] = True
                                        botElements['lastSide'] = reverseSide[botElements['guessSide']]
                                elif not botElements['guessSideStatus'] and getKDJ['side'] != reverseSide[botElements['guessSide']]:
                                    botElements['firstTypeTrigger'] = 0
                                botElements['guessSideRetry'] += 1

                                if botElements['guessSideRetry'] == int(config('SETTING', 'GUESS_SIDE_RETRY')):
                                    klineConnect = True
                                    klineConnectCount = 0
                                    klines1DAY = {}
                                    while klineConnect:
                                        try:
                                            klines1DAY = client.futures_klines(symbol=getBot['parity'], interval=Client.KLINE_INTERVAL_1DAY, limit=2)
                                            klineConnect = False
                                        except Exception as e:
                                            klineConnectCount += 1
                                            if ("Max retries exceeded" in str(e) or "Too many requests" in str(e) or "recvWindow" in str(e) or "Connection broken" in str(e)) and klineConnectCount < 3:
                                                time.sleep(float(config('SETTING', 'TIME_SLEEP')))
                                            elif "Way too many requests" in str(e) or "Read timed out." in str(e) or (3 <= klineConnectCount <= 6):
                                                proxyOrder = requests.post(url + 'proxy-order/' + str(getBot['bot']), headers={
                                                    'neresi': 'dogunun+billurlari'
                                                }).json()
                                                client = Client(str(getBot['api_key']), str(getBot['api_secret']), {"timeout": 300, 'proxies': proxyOrder})
                                            else:
                                                raise Exception(e)
                                    botElements['guessSide'] = sideCalc(klines1DAY)
                                    botElements['guessSideRetry'] = 0

                    sameTest = {
                        'K': getKDJ['K'],
                        'D': getKDJ['D'],
                        'J': getKDJ['J']
                    }
                    # SYNC BOT
                    syncBotWhile = True
                    syncBotCount = 0
                    while syncBotWhile:
                        syncBot = requests.post(url + 'get-order/' + getBot['bot'], headers={
                            'neresi': 'dogunun+billurlari'
                        })
                        if syncBot.status_code == 200:
                            if syncBot.json()['status'] == 0:
                                raise Exception('bot_change')
                            else:
                                for bt in syncBot.json().keys():
                                    getBot[bt] = syncBot.json()[bt]
                            syncBotWhile = False
                        elif syncBotCount >= int(config('API', 'ERR_COUNT')):
                            raise Exception('server_error')
                        else:
                            syncBotCount += 1
                    # SYNC BOT END

                    if botElements['lastSide'] == 'HOLD' and getBot['status'] == 2 and botElements['lastPrice'] == 0:
                        setBotWhile = True
                        setBotCount = 0
                        while setBotWhile:
                            setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                                'neresi': 'dogunun+billurlari'
                            }, json={
                                'line': getframeinfo(currentframe()).lineno,
                                'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                'KDJ': getKDJ['type'],
                                'MACD': botElements['lastMAC'],
                                'action': 'STOP',
                            })
                            if setBot.status_code == 200:
                                setBotWhile = False
                            elif setBotCount >= int(config('API', 'ERR_COUNT')):
                                raise Exception('server_error')
                            else:
                                time.sleep(1)
                                setBotCount += 1
                        raise Exception('STOP')
                    else:
                        if getBot['status'] == 2 and botElements['orderStatus'] == False:
                            operationLoop = False
                            setBotWhile = True
                            setBotCount = 0
                            while setBotWhile:
                                setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                                    'neresi': 'dogunun+billurlari'
                                }, json={
                                    'line': getframeinfo(currentframe()).lineno,
                                    'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    'KDJ': getKDJ['type'],
                                    'MACD': botElements['lastMAC'],
                                    'side': botElements['lastSide'],
                                    'action': 'CLOSE',
                                })
                                if setBot.status_code == 200:
                                    setBotWhile = False
                                elif setBotCount >= int(config('API', 'ERR_COUNT')):
                                    raise Exception('server_error')
                                else:
                                    time.sleep(1)
                                    setBotCount += 1
                        else:
                            # START ORDER
                            if botElements['lastSide'] != getKDJ['side'] and botElements['firstTypeTrigger'] >= int(config('SETTING', 'FIRST_FAKE')) and botElements['fakeTrigger'] >= int(config('SETTING', 'FAKE_TRIGGER')) and botElements['orderStatus'] == False:
                                botElements['lastPrice'] = float(client.futures_ticker(symbol=getBot['parity'])['lastPrice'])
                                if botElements['lastSide'] != 'HOLD' and botElements['profitTrigger'] == False and botElements['orderStatus'] == True:
                                    positionConnect = True
                                    positionConnectCount = 0
                                    try:
                                        position = getPosition(client, getBot['parity'], botElements['lastType'])
                                        positionConnect = False
                                    except Exception as e:
                                        positionConnectCount += 1
                                        if ("Max retries exceeded" in str(e) or "Too many requests" in str(e) or "recvWindow" in str(e) or "Connection broken" in str(e)) and positionConnectCount < 3:
                                            time.sleep(float(config('SETTING', 'TIME_SLEEP')))
                                        elif "Way too many requests" in str(e) or "Read timed out." in str(e) or (3 <= positionConnectCount <= 6):
                                            proxyOrder = requests.post(url + 'proxy-order/' + str(getBot['bot']), headers={
                                                'neresi': 'dogunun+billurlari'
                                            }).json()
                                            client = Client(str(getBot['api_key']), str(getBot['api_secret']), {"timeout": 40, 'proxies': proxyOrder})
                                        else:
                                            raise Exception(e)

                                    if position['amount'] > 0:
                                        # Binance
                                        botElements['orderStatus'] = False
                                        jsonData(getBot['bot'], 'SET', botElements)
                                        client.futures_create_order(symbol=getBot['parity'], side=getKDJ['side'], positionSide=botElements['lastType'], type="MARKET", quantity=botElements['lastQuantity'])
                                        # Binance END
                                        setBotWhile = True
                                        setBotCount = 0
                                        while setBotWhile:
                                            setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                                                'neresi': 'dogunun+billurlari'
                                            }, json={
                                                'line': getframeinfo(currentframe()).lineno,
                                                'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                'KDJ': getKDJ['type'],
                                                'MACD': botElements['lastMAC'],
                                                'side': botElements['lastSide'],
                                                'price': position['markPrice'],
                                                'profit': position['profit'],
                                                'quantity': position['amount'],
                                                'action': 'CLOSE',
                                            })
                                            if setBot.status_code == 200:
                                                setBotWhile = False
                                            elif setBotCount >= int(config('API', 'ERR_COUNT')):
                                                raise Exception('server_error')
                                            else:
                                                time.sleep(1)
                                                setBotCount += 1
                                    else:
                                        setBotWhile = True
                                        setBotCount = 0
                                        while setBotWhile:
                                            setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                                                'neresi': 'dogunun+billurlari'
                                            }, json={
                                                'line': getframeinfo(currentframe()).lineno,
                                                'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                'KDJ': getKDJ['type'],
                                                'MACD': botElements['lastMAC'],
                                                'side': botElements['lastSide'],
                                                'action': 'MANUAL_STOP',
                                            })
                                            if setBot.status_code == 200:
                                                setBotWhile = False
                                            elif setBotCount >= int(config('API', 'ERR_COUNT')):
                                                raise Exception('server_error')
                                            else:
                                                time.sleep(1)
                                                setBotCount += 1
                                        raise Exception('manual_stop')
                                else:
                                    botElements['profitTrigger'] = False

                                if getBot['status'] == 2:
                                    operationLoop = False
                                    setBotWhile = True
                                    setBotCount = 0
                                    while setBotWhile:
                                        setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                                            'neresi': 'dogunun+billurlari'
                                        }, json={
                                            'line': getframeinfo(currentframe()).lineno,
                                            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                            'KDJ': getKDJ['type'],
                                            'MACD': botElements['lastMAC'],
                                            'side': botElements['lastSide'],
                                            'action': 'CLOSE',
                                        })
                                        if setBot.status_code == 200:
                                            setBotWhile = False
                                        elif setBotCount >= int(config('API', 'ERR_COUNT')):
                                            raise Exception('server_error')
                                        else:
                                            time.sleep(1)
                                            setBotCount += 1
                                else:
                                    botElements['lastSide'] = getKDJ['side']
                                    botElements['lastType'] = getKDJ['type']
                                    botElements['lastMAC'] = None
                                    botElements['firstLogin'] = False
                                    # Binance
                                    botElements['balance'] = getOrderBalance(client, "USDT", int(getBot['percent']))

                                    # profit trigger
                                    botElements['maxDamageUSDT'] = round((botElements['balance'] / 100) * int(getBot['MAX_DAMAGE_USDT_PERCENT']), 2)
                                    botElements['maxDamageCount'] = 0
                                    botElements['maxDamageBefore'] = 0

                                    botElements['maxProfit'] = round((botElements['balance'] / 100) * profitMax(klines), 2)
                                    botElements['maxProfitCount'] = 0
                                    botElements['maxProfitStatus'] = False
                                    botElements['maxProfitMax'] = 0
                                    botElements['maxProfitMin'] = 0
                                    botElements['setLeverage'] = True
                                    botElements['DEMATriggerStatus'] = False

                                    # profit trigger END

                                    botElements['lastQuantity'] = "{:0.0{}f}".format(float((botElements['balance'] / botElements['lastPrice']) * getBot['leverage']), fractions[getBot['parity']])
                                    if float(botElements['lastQuantity']) <= 0:
                                        raise Exception("Bakiye hatası")
                                    client.futures_create_order(symbol=getBot['parity'], side=botElements['lastSide'], type='MARKET', quantity=botElements['lastQuantity'], positionSide=botElements['lastType'])
                                    # Binance END
                                    botElements['orderStatus'] = True
                                    jsonData(getBot['bot'], 'SET', botElements)
                                    setBotWhile = True
                                    setBotCount = 0
                                    while setBotWhile:
                                        setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                                            'neresi': 'dogunun+billurlari'
                                        }, json={
                                            'line': getframeinfo(currentframe()).lineno,
                                            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                            'KDJ': getKDJ['type'],
                                            'MACD': botElements['lastMAC'],
                                            'side': botElements['lastSide'],
                                            'position': botElements['lastType'],
                                            'balance': botElements['balance'],
                                            'quantity': botElements['lastQuantity'],
                                            'price': botElements['lastPrice'],
                                            'action': 'OPEN',
                                        })
                                        if setBot.status_code == 200:
                                            setBotWhile = False
                                        elif setBotCount >= int(config('API', 'ERR_COUNT')):
                                            raise Exception('server_error')
                                        else:
                                            time.sleep(1)
                                            setBotCount += 1
                            else:
                                if not botElements['orderStatus']:
                                    setBotWhile = True
                                    setBotCount = 0
                                    while setBotWhile:
                                        setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                                            'neresi': 'dogunun+billurlari'
                                        }, json={
                                            'line': getframeinfo(currentframe()).lineno,
                                            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                            'KDJ': getKDJ['type'],
                                            'MACD': botElements['lastMAC'],
                                            'action': 'ORDER_START_WAITING',
                                        })
                                        if setBot.status_code == 200:
                                            setBotWhile = False
                                        elif setBotCount >= int(config('API', 'ERR_COUNT')):
                                            raise Exception('server_error')
                                        else:
                                            time.sleep(1)
                                            setBotCount += 1
                                elif botElements['lastPrice'] != 0 and botElements['profitTrigger'] == False and botElements['orderStatus'] == True:
                                    macdConnect = True
                                    macdConnectCount = 0
                                    try:
                                        position = getPosition(client, getBot['parity'], botElements['lastType'])
                                        # short / long
                                        botElements['lastMAC'] = mac_dema(klines, getBot['dema_short'], getBot['dema_long'], getBot['dema_signal'], botElements['lastMAC'])
                                        jsonData(getBot['bot'], 'SET', botElements)
                                        macdConnect = False
                                    except Exception as e:
                                        macdConnectCount += 1
                                        if ("Max retries exceeded" in str(e) or "Too many requests" in str(e) or "recvWindow" in str(e) or "Connection broken" in str(e)) and macdConnectCount < 3:
                                            time.sleep(float(config('SETTING', 'TIME_SLEEP')))
                                        elif "Way too many requests" in str(e) or "Read timed out." in str(e) or (3 <= macdConnectCount <= 6):
                                            proxyOrder = requests.post(url + 'proxy-order/' + str(getBot['bot']), headers={
                                                'neresi': 'dogunun+billurlari'
                                            }).json()
                                            client = Client(str(getBot['api_key']), str(getBot['api_secret']), {"timeout": 40, 'proxies': proxyOrder})
                                        else:
                                            raise Exception(e)
                                    if botElements['setLeverage']:
                                        botElements['maxDamageUSDT'] = botElements['maxDamageUSDT'] * position['leverage']
                                        botElements['setLeverage'] = False
                                        jsonData(getBot['bot'], 'SET', botElements)
                                    if position['amount'] <= 0:
                                        raise Exception('close')
                                    elif position['profit'] > 0:
                                        botElements['maxDamageCount'] = 0
                                        if position['profit'] >= int((botElements['balance'] / 100) * int(config('SETTING', 'DEMA_TRIGGER_PROFIT'))):
                                            botElements['DEMATriggerStatus'] = True
                                        elif not botElements['DEMATriggerStatus']:
                                            botElements['lastMAC'] = None

                                        # Max Profit
                                        if position['profit'] >= botElements['maxProfit']:
                                            botElements['maxProfitStatus'] = True
                                        if position['profit'] > botElements['maxProfitMax']:
                                            botElements['maxProfitMax'] = position['profit']
                                            botElements['maxProfitMin'] = round(botElements['maxProfitMax'] - ((botElements['maxProfitMax'] / 100) * int(config('SETTING', 'MAX_PROFIT_PERCENT'))), 2)
                                            botElements['maxProfitCount'] = 0
                                        # Max Profit Max
                                        if botElements['lastMAC'] == reverseType[botElements['lastType']] and botElements['DEMATriggerStatus'] == True:
                                            botElements['profitTriggerKey'] = "TRIGGER_MACDDEMA"
                                            botElements['profitTurn'] = True
                                        elif botElements['maxProfitMin'] >= position['profit'] and botElements['maxProfitStatus'] == True:
                                            if botElements['maxProfitCount'] >= int(config('SETTING', 'MAX_PROFIT_COUNT')):
                                                botElements['profitTriggerKey'] = "TRIGGER_PROFIT_EXIT"
                                                botElements['profitTurn'] = True
                                            else:
                                                botElements['maxProfitCount'] += 1
                                    elif position['profit'] < 0:
                                        botElements['maxProfitStatus'] = False
                                        if abs(position['profit']) >= int((botElements['balance'] / 100) * int(config('SETTING', 'DEMA_TRIGGER_DAMAGE'))):
                                            botElements['DEMATriggerStatus'] = True
                                        elif not botElements['DEMATriggerStatus']:
                                            botElements['lastMAC'] = None
                                        if botElements['lastMAC'] == reverseType[botElements['lastType']] and botElements['DEMATriggerStatus'] == True:
                                            botElements['profitTriggerKey'] = "TRIGGER_MACDDEMA"
                                            botElements['profitTurn'] = True
                                        elif abs(position['profit']) >= botElements['maxDamageUSDT']:
                                            if botElements['maxDamageBefore'] < abs(position['profit']):
                                                botElements['maxDamageCount'] += 1
                                                if botElements['maxDamageCount'] >= int(config('SETTING', 'MAX_DAMAGE_COUNT')):
                                                    botElements['profitTriggerKey'] = "MAX_DAMAGE"
                                                    botElements['profitTurn'] = True
                                            else:
                                                botElements['maxDamageCount'] = 0
                                            botElements['maxDamageBefore'] = abs(position['profit'])
                                    jsonData(getBot['bot'], 'SET', botElements)
                                    if botElements['profitTurn']:
                                        botElements['profitTurn'] = False
                                        botElements['lastSide'] = getKDJ['side']
                                        botElements['fakeTrigger'] = 0
                                        botElements['profitTrigger'] = True
                                        botElements['orderStatus'] = False
                                        jsonData(getBot['bot'], 'SET', botElements)
                                        client.futures_create_order(symbol=getBot['parity'], side='SELL' if botElements['lastType'] == 'LONG' else "BUY", positionSide=botElements['lastType'], type="MARKET", quantity=botElements['lastQuantity'])
                                        setBotWhile = True
                                        setBotCount = 0
                                        while setBotWhile:
                                            setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                                                'neresi': 'dogunun+billurlari'
                                            }, json={
                                                'line': getframeinfo(currentframe()).lineno,
                                                'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                'KDJ': getKDJ['type'],
                                                'MACD': botElements['lastMAC'],
                                                'side': botElements['lastSide'],
                                                'price': position['markPrice'],
                                                'profit': position['profit'],
                                                'quantity': position['amount'],
                                                'action': botElements['profitTriggerKey'],
                                            })
                                            if setBot.status_code == 200:
                                                setBotWhile = False
                                            elif setBotCount >= int(config('API', 'ERR_COUNT')):
                                                raise Exception('server_error')
                                            else:
                                                time.sleep(1)
                                                setBotCount += 1
                                    # emir bozma yeri
                    # Max Request Sleep
                    time.sleep(float(config('SETTING', 'TIME_SLEEP')))
                    # Max Request Sleep
                else:
                    time.sleep(float(config('SETTING', 'TIME_SLEEP')))
            except Exception as exception:
                operationLoop = False
                getBot['status'] = 0
                print("emir kapatıldı!!")
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

                errBotWhile = True
                errBotCount = 0
                while errBotWhile:
                    errBot = requests.post(url + 'set-error', headers={
                    'neresi': 'dogunun+billurlari'
                }, json={
                    'bot': getBot['bot'],
                    'errors': [
                        str(exc_type),
                        str(fname),
                        str(exc_tb.tb_lineno),
                        str(exception)
                    ]
                })
                    if errBot.status_code == 200:
                        errBotWhile = False
                    elif errBotCount >= int(config('API', 'ERR_COUNT')):
                        raise Exception('server_error')
                    else:
                        time.sleep(1)
                        errBotCount += 1
                if getBot['version'] != version:
                    print("yeniden başlatma")
                    os.execl(sys.executable, sys.executable, *sys.argv)
            except KeyboardInterrupt:
                requests.post(url + 'delete-bots', headers={
                    'neresi': 'dogunun+billurlari'
                })
                sys.exit(0)
    except Exception as exception:
        logging.error(str(exception))
