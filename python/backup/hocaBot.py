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


def profitMax(klines, leverage):
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
    high.pop(0)
    low = list(df['Low'])
    low.reverse()
    low.pop(0)
    diffs = []
    for key in range(0, 10):
        diffs.append(get_diff(float(low[key]), float(high[key])))
    minDiff = int(min(diffs) * leverage)
    maxDiff = int(max(diffs) * leverage)
    averageDiff = int((sum(diffs) / len(diffs)) * leverage)
    return {
        'profit': {
            maxDiff: {
                'count': 3,
                'percent': 15,
            },
            averageDiff: {
                'count': 4,
                'percent': 30,
            },
            minDiff: {
                'count': 4,
                'percent': 40,
            },
        },
        'default': minDiff
    }


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
        with open(os.path.dirname(os.path.realpath(__file__)) + "/datas/" + bot + '.json', 'w+') as outfile:
            outfile.write(json.dumps(data))
        return True
    elif status == 'DELETE':
        try:
            os.remove((os.path.dirname(os.path.realpath(__file__)) + "/datas/" + bot + '.json'))
            return True
        except:
            return False
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
            'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
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
                if ("Max retries exceeded" in str(e) or "Too many requests" in str(e) or "recvWindow" in str(e) or "Connection broken" in str(e) or "Please try again" in str(e) or "Invalid JSON" in str(e)) and clientConnectCount < 3:
                    time.sleep(float(config('SETTING', 'TIME_SLEEP')))
                elif "Way too many requests" in str(e) or "Read timed out." in str(e) or (3 <= clientConnectCount <= 6):
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
        if getBot['transfer'] is not None:
            botElements = jsonData(getBot['transfer'], 'GET')
            if not botElements:
                errBotWhile = True
                errBotCount = 0
                while errBotWhile:
                    errBot = requests.post(url + 'set-error', headers={
                        'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                    }, json={
                        'bot': getBot['bot'],
                        'errors': [
                            "ilerleme dosyasi bulunamadi.",
                            getBot['transfer'],
                            getBot['bot'],
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
                    if ("Max retries exceeded" in str(e) or "Too many requests" in str(e) or "recvWindow" in str(e) or "Connection broken" in str(e) or "Please try again" in str(e) or "Invalid JSON" in str(e)) and klineConnectCount < 3:
                        time.sleep(float(config('SETTING', 'TIME_SLEEP')))
                    elif "Way too many requests" in str(e) or "Read timed out." in str(e) or (3 <= klineConnectCount <= 6):
                        proxyOrder = requests.post(url + 'proxy-order/' + str(getBot['bot']), headers={
                            'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                        }).json()
                        client = Client(str(getBot['api_key']), str(getBot['api_secret']), {"timeout": 300, 'proxies': proxyOrder})
                    else:
                        raise Exception(e)
            botElements = {
                'lastPrice': 0,
                'lastSide': 'HOLD',
                'guessSide': 'HOLD',  # sideCalc(klines1DAY),
                'guessSideStatus': False,
                'guessSideRetry': int(config('SETTING', 'GUESS_SIDE_RETRY')),
                'lastType': None,
                'orderStatus': False,
                'profitTurn': False,
                'profitTriggerKey': None,
                'firstTypeTrigger': 0,
                'fakeTrigger': 0,
                'fakeTriggerK': [],
                'fakeTriggerSide': 'HOLD',
                'maxDamageUSDT': 0,
                'maxDamageCount': 0,
                'maxDamageBefore': 0,
                'lastProfitOuts': [],
                'maxProfit': 100,
                'maxProfitCount': 0,
                'maxProfitCountMax': 0,
                'maxProfitStatus': False,
                'maxProfitMax': 0,
                'maxProfitMin': 0,
                'lastQuantity': None,
                'profitTrigger': False,
                'newTriggerOrder': False,
                'balance': 0,
                'setLeverage': True,
                'firstLogin': True,
                'KDJtriggerCheck': 0,
                'KDJtriggerCheckReverse': 0,
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
                        klines = client.futures_klines(symbol=getBot['parity'], interval=client.KLINE_INTERVAL_1HOUR, limit=150)
                        klineConnect = False
                    except Exception as e:
                        klineConnectCount += 1
                        if ("Max retries exceeded" in str(e) or "Too many requests" in str(e) or "recvWindow" in str(e) or "Connection broken" in str(e) or "Please try again" in str(e) or "Invalid JSON" in str(e)) and klineConnectCount < 3:
                            time.sleep(float(config('SETTING', 'TIME_SLEEP')))
                        elif "Way too many requests" in str(e) or "Read timed out." in str(e) or (3 <= klineConnectCount <= 6):
                            proxyOrder = requests.post(url + 'proxy-order/' + str(getBot['bot']), headers={
                                'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                            }).json()
                            client = Client(str(getBot['api_key']), str(getBot['api_secret']), {"timeout": 300, 'proxies': proxyOrder})
                        else:
                            raise Exception(e)
                getKDJ = get_kdj(klines, getBot['kdj_period'], getBot['kdj_signal'], botElements['lastSide'], float(getBot['KDJ_X']))
                if getKDJ['K'] != sameTest['K'] or getKDJ['D'] != sameTest['D'] or getKDJ['J'] != sameTest['J']:
                    sameTest = {
                        'K': getKDJ['K'],
                        'D': getKDJ['D'],
                        'J': getKDJ['J']
                    }
                    if not botElements['orderStatus']:
                        # first side check
                        if botElements['firstTypeTrigger'] <= int(config('SETTING', 'FIRST_FAKE')):
                            if botElements['lastSide'] == getKDJ['side']:
                                botElements['firstTypeTrigger'] += 1
                            else:
                                botElements['firstTypeTrigger'] = 0
                            botElements['lastSide'] = getKDJ['side']
                        # first side check END
                        if botElements['fakeTriggerSide'] == getKDJ['side'] and botElements['firstTypeTrigger'] >= int(config('SETTING', 'FIRST_FAKE')):
                            if len(botElements['fakeTriggerK']) > 0:
                                if getKDJ['side'] == 'BUY' and botElements['fakeTriggerK'][-1] < float(getKDJ['K']):
                                    botElements['fakeTrigger'] += 1
                                    botElements['fakeTriggerK'].append(float(getKDJ['K']))
                                elif getKDJ['side'] == 'SELL' and botElements['fakeTriggerK'][-1] > float(getKDJ['K']):
                                    botElements['fakeTrigger'] += 1
                                    botElements['fakeTriggerK'].append(float(getKDJ['K']))
                            else:
                                botElements['fakeTriggerK'].append(float(getKDJ['K']))
                        else:
                            botElements['fakeTrigger'] = 0
                            botElements['fakeTriggerK'] = []
                        botElements['fakeTriggerSide'] = getKDJ['side']
                        jsonData(getBot['bot'], 'SET', botElements)

                    # SYNC BOT
                    syncBotWhile = True
                    syncBotCount = 0
                    while syncBotWhile:
                        syncBot = requests.post(url + 'get-order/' + getBot['bot'], headers={
                            'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                        })
                        if syncBot.status_code == 200:
                            if syncBot.json()['status'] == 0:
                                sys.exit(0)
                            else:
                                for bt in syncBot.json().keys():
                                    getBot[bt] = syncBot.json()[bt]
                            syncBotWhile = False
                        elif syncBotCount >= int(config('API', 'ERR_COUNT')):
                            raise Exception('server_error')
                        else:
                            syncBotCount += 1
                    # SYNC BOT END
                    if getBot['status'] == 2 and botElements['orderStatus'] == False:
                        operationLoop = False
                        setBotWhile = True
                        setBotCount = 0
                        while setBotWhile:
                            setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                                'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                            }, json={
                                'line': getframeinfo(currentframe()).lineno,
                                'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                'KDJ': getKDJ['type'],
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
                                    if ("Max retries exceeded" in str(e) or "Too many requests" in str(e) or "recvWindow" in str(e) or "Connection broken" in str(e) or "Please try again" in str(e) or "Invalid JSON" in str(e)) and positionConnectCount < 3:
                                        time.sleep(float(config('SETTING', 'TIME_SLEEP')))
                                    elif "Way too many requests" in str(e) or "Read timed out." in str(e) or (3 <= positionConnectCount <= 6):
                                        proxyOrder = requests.post(url + 'proxy-order/' + str(getBot['bot']), headers={
                                            'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                                        }).json()
                                        client = Client(str(getBot['api_key']), str(getBot['api_secret']), {"timeout": 40, 'proxies': proxyOrder})
                                    else:
                                        raise Exception(e)
                                if position['amount'] > 0:
                                    # Binance
                                    botElements['orderStatus'] = False
                                    jsonData(getBot['bot'], 'SET', botElements)

                                    orderCreate = True
                                    orderCreateCount = 0
                                    while orderCreate:
                                        try:
                                            client.futures_create_order(symbol=getBot['parity'], side=getKDJ['side'], positionSide=botElements['lastType'], type="MARKET", quantity=botElements['lastQuantity'])
                                            orderCreate = False
                                        except Exception as e:
                                            orderCreateCount += 1
                                            if ("Max retries exceeded" in str(e) or "Too many requests" in str(e) or "recvWindow" in str(e) or "Connection broken" in str(e) or "Please try again" in str(e) or "Invalid JSON" in str(e)) and orderCreateCount < 3:
                                                time.sleep(float(config('SETTING', 'TIME_SLEEP')))
                                            elif "Way too many requests" in str(e) or "Read timed out." in str(e) or (3 <= orderCreateCount <= 6):
                                                proxyOrder = requests.post(url + 'proxy-order/' + str(getBot['bot']), headers={
                                                    'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                                                }).json()
                                                getBot['proxy'] = proxyOrder['proxy']
                                            else:
                                                raise Exception(e)

                                    # Binance END
                                    setBotWhile = True
                                    setBotCount = 0
                                    while setBotWhile:
                                        setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                                            'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                                        }, json={
                                            'line': getframeinfo(currentframe()).lineno,
                                            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                            'KDJ': getKDJ['type'],
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
                                            'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                                        }, json={
                                            'line': getframeinfo(currentframe()).lineno,
                                            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                            'KDJ': getKDJ['type'],
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
                                        'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                                    }, json={
                                        'line': getframeinfo(currentframe()).lineno,
                                        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        'KDJ': getKDJ['type'],
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
                                botElements['firstLogin'] = False
                                # Binance
                                botElements['balance'] = getOrderBalance(client, "USDT", int(getBot['percent']))

                                # profit trigger
                                botElements['maxDamageUSDT'] = round((botElements['balance'] / 100) * int(getBot['MAX_DAMAGE_USDT_PERCENT']), 2)
                                botElements['maxDamageCount'] = 0
                                botElements['maxDamageBefore'] = 0
                                botElements['profitMax'] = profitMax(klines, int(getBot['leverage']))

                                botElements['maxProfit'] = round((botElements['balance'] / 100) * botElements['profitMax']['default'], 2)
                                botElements['maxProfitCount'] = 0
                                botElements['maxProfitCountMax'] = 0
                                botElements['maxProfitStatus'] = False
                                botElements['maxProfitMax'] = 0
                                botElements['maxProfitMin'] = 0
                                botElements['setLeverage'] = True

                                # profit trigger END

                                botElements['lastQuantity'] = "{:0.0{}f}".format(float((botElements['balance'] / botElements['lastPrice']) * getBot['leverage']), fractions[getBot['parity']])
                                if float(botElements['lastQuantity']) <= 0:
                                    raise Exception("Bakiye hatası")

                                orderCreate = True
                                orderCreateCount = 0
                                while orderCreate:
                                    try:
                                        client.futures_create_order(symbol=getBot['parity'], side=botElements['lastSide'], type='MARKET', quantity=botElements['lastQuantity'], positionSide=botElements['lastType'])
                                        orderCreate = False
                                    except Exception as e:
                                        orderCreateCount += 1
                                        if ("Max retries exceeded" in str(e) or "Too many requests" in str(e) or "recvWindow" in str(e) or "Connection broken" in str(e) or "Please try again" in str(e) or "Invalid JSON" in str(e)) and orderCreateCount < 3:
                                            time.sleep(float(config('SETTING', 'TIME_SLEEP')))
                                        elif "Way too many requests" in str(e) or "Read timed out." in str(e) or (3 <= orderCreateCount <= 6):
                                            proxyOrder = requests.post(url + 'proxy-order/' + str(getBot['bot']), headers={
                                                'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                                            }).json()
                                            getBot['proxy'] = proxyOrder['proxy']
                                        else:
                                            raise Exception(e)

                                # Binance END
                                botElements['orderStatus'] = True
                                jsonData(getBot['bot'], 'SET', botElements)
                                setBotWhile = True
                                setBotCount = 0
                                while setBotWhile:
                                    setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                                        'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                                    }, json={
                                        'line': getframeinfo(currentframe()).lineno,
                                        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        'KDJ': getKDJ['type'],
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
                                        'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                                    }, json={
                                        'line': getframeinfo(currentframe()).lineno,
                                        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        'KDJ': getKDJ['type'],
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
                                positionConnect = True
                                positionConnectCount = 0
                                try:
                                    position = getPosition(client, getBot['parity'], botElements['lastType'])
                                    positionConnect = False
                                except Exception as e:
                                    positionConnectCount += 1
                                    if ("Max retries exceeded" in str(e) or "Too many requests" in str(e) or "recvWindow" in str(e) or "Connection broken" in str(e) or "Please try again" in str(e) or "Invalid JSON" in str(e)) and positionConnectCount < 3:
                                        time.sleep(float(config('SETTING', 'TIME_SLEEP')))
                                    elif "Way too many requests" in str(e) or "Read timed out." in str(e) or (3 <= positionConnectCount <= 6):
                                        proxyOrder = requests.post(url + 'proxy-order/' + str(getBot['bot']), headers={
                                            'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                                        }).json()
                                        client = Client(str(getBot['api_key']), str(getBot['api_secret']), {"timeout": 40, 'proxies': proxyOrder})
                                    else:
                                        raise Exception(e)

                                if botElements['lastSide'] == getKDJ['side']:
                                    botElements['KDJtriggerCheck'] += 1
                                elif botElements['KDJtriggerCheck'] <= 5:
                                    botElements['KDJtriggerCheckReverse'] += 1

                                if botElements['setLeverage']:
                                    botElements['maxDamageUSDT'] = botElements['maxDamageUSDT'] * position['leverage']
                                    botElements['setLeverage'] = False
                                    jsonData(getBot['bot'], 'SET', botElements)
                                if position['amount'] <= 0:
                                    raise Exception('close')
                                elif position['profit'] > 0:
                                    botElements['maxDamageCount'] = 0

                                    # Max Profit
                                    if position['profit'] >= botElements['maxProfit']:
                                        botElements['maxProfitStatus'] = True

                                    if position['profit'] > botElements['maxProfitMax']:
                                        botElements['maxProfitMax'] = position['profit']
                                        botElements['maxProfitCount'] = 0
                                        profitTriggerStatus = True
                                        for attr, value in botElements['profitMax']['profit'].items():
                                            if ((botElements['balance'] / 100) * attr) >= botElements['maxProfitMax'] and profitTriggerStatus == True:
                                                profitTriggerStatus = False
                                                botElements['maxProfitCountMax'] = value['count']
                                                botElements['maxProfitMin'] = round(botElements['maxProfitMax'] - ((botElements['maxProfitMax'] / 100) * value['percent']), 2)

                                    # Max Profit Max
                                    if botElements['maxProfitMin'] >= position['profit'] and botElements['maxProfitStatus'] == True:
                                        if botElements['maxProfitCount'] >= botElements['maxProfitCountMax']:
                                            botElements['profitTriggerKey'] = "TRIGGER_PROFIT_EXIT"
                                            botElements['profitTurn'] = True
                                        else:
                                            if len(botElements['lastProfitOuts']) == 0:
                                                botElements['lastProfitOuts'].append(position['profit'])
                                                botElements['maxProfitCount'] += 1
                                            elif botElements['lastProfitOuts'][-1] > position['profit']:
                                                botElements['lastProfitOuts'].append(position['profit'])
                                                botElements['maxProfitCount'] += 1
                                            elif botElements['lastProfitOuts'][-1] < position['profit']:
                                                for last in botElements['lastProfitOuts']:
                                                    if position['profit'] > last:
                                                        botElements['lastProfitOuts'].remove(last)
                                                        botElements['maxProfitCount'] -= 1
                                                if botElements['maxProfitCount'] < 0:
                                                    botElements['maxProfitCount'] = 0
                                    else:
                                        botElements['maxProfitCount'] = 0
                                        botElements['lastProfitOuts'] = []

                                elif position['profit'] < 0:
                                    botElements['maxProfitStatus'] = False
                                    if abs(position['profit']) >= botElements['maxDamageUSDT']:
                                        if botElements['maxDamageBefore'] < abs(position['profit']):
                                            botElements['maxDamageCount'] += 1
                                            if botElements['maxDamageCount'] >= int(config('SETTING', 'MAX_DAMAGE_COUNT')):
                                                botElements['profitTriggerKey'] = "MAX_DAMAGE"
                                                botElements['profitTurn'] = True
                                        else:
                                            botElements['maxDamageCount'] = 0
                                        botElements['maxDamageBefore'] = abs(position['profit'])
                                jsonData(getBot['bot'], 'SET', botElements)

                                if botElements['lastSide'] != getKDJ['side'] and (botElements['KDJtriggerCheck'] >= int(config('SETTING', 'CLOSE_ORDER_KDJ')) or botElements['KDJtriggerCheckReverse'] >= int(config('SETTING', 'CLOSE_ORDER_KDJ_REVERSE'))):
                                    botElements['profitTurn'] = True
                                    botElements['profitTriggerKey'] = "KDJ_TRIGGER"

                                if botElements['profitTurn']:
                                    botElements['KDJtriggerCheck'] = 0
                                    botElements['KDJtriggerCheckReverse'] = 0
                                    botElements['profitTurn'] = False
                                    botElements['fakeTrigger'] = 0
                                    botElements['profitTrigger'] = True
                                    botElements['orderStatus'] = False
                                    jsonData(getBot['bot'], 'SET', botElements)

                                    orderCreate = True
                                    orderCreateCount = 0
                                    while orderCreate:
                                        try:
                                            client.futures_create_order(symbol=getBot['parity'], side='SELL' if botElements['lastType'] == 'LONG' else "BUY", positionSide=botElements['lastType'], type="MARKET", quantity=botElements['lastQuantity'])
                                            orderCreate = False
                                        except Exception as e:
                                            orderCreateCount += 1
                                            if ("Max retries exceeded" in str(e) or "Too many requests" in str(e) or "recvWindow" in str(e) or "Connection broken" in str(e) or "Please try again" in str(e) or "Invalid JSON" in str(e)) and orderCreateCount < 3:
                                                time.sleep(float(config('SETTING', 'TIME_SLEEP')))
                                            elif "Way too many requests" in str(e) or "Read timed out." in str(e) or (3 <= orderCreateCount <= 6):
                                                proxyOrder = requests.post(url + 'proxy-order/' + str(getBot['bot']), headers={
                                                    'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                                                }).json()
                                                getBot['proxy'] = proxyOrder['proxy']
                                            else:
                                                raise Exception(e)

                                    setBotWhile = True
                                    setBotCount = 0
                                    while setBotWhile:
                                        setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                                            'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                                        }, json={
                                            'line': getframeinfo(currentframe()).lineno,
                                            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                            'KDJ': getKDJ['type'],
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
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

                errBotWhile = True
                errBotCount = 0
                while errBotWhile:
                    errBot = requests.post(url + 'set-error', headers={
                        'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
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
                    'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                })
                sys.exit(0)
    except Exception as exception:
        logging.error(str(exception))
        requests.post(url + 'delete-bots', headers={
            'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
        })
        sys.exit(0)
