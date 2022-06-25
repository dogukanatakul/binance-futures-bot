import time, sys, os, requests, uuid, talib, numpy
from datetime import datetime
from binance.client import Client
import pandas as pd
import json
from helper import config
from inspect import currentframe, getframeinfo
import logging

url = config('API', 'SITE')


def brs(klines, M=0, T=0):
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
    BRS = (((list(df['Close'])[-1] - (sum(df['Low']) / len(df['Low']))) / ((sum(df['High']) / len(df['High'])) - (sum(df['Low']) / len(df['Low'])))) * 100) * 1
    M = 2.5 / 3 * M + 0.5 / 3 * BRS
    T = 2.5 / 3 * T + 0.5 / 3 * M
    C = 3 * M - 2 * T

    if C > T:
        result = {
            'type': 'LONG',
            'side': 'BUY',
            'BRS': BRS,
            'M': M,
            'T': T,
            'C': C,
        }
    else:
        result = {
            'type': 'SHORT',
            'side': 'SELL',
            'BRS': BRS,
            'M': M,
            'T': T,
            'C': C,
        }
    return result


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
                if ("Max retries exceeded" in str(e) or "Too many requests" in str(e) or "recvWindow" in str(e) or "Connection broken" in str(e) or "Please try again" in str(e)) and clientConnectCount < 3:
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
            'M': 0,
            'T': 0,
            'C': 0
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
            botElements = {
                'lastPrice': 0,
                'lastSide': 'HOLD',
                'lastType': None,
                'orderStatus': False,
                'profitTurn': False,
                'triggerKey': None,
                'maxDamageUSDT': 0,
                'maxDamageCount': 0,
                'maxDamageBefore': 0,
                'lastQuantity': None,
                'newTriggerOrder': False,
                'balance': 0,
                'setLeverage': True,
                'firstLogin': True,
                'BRS_M': getBot['BRS_M'],
                'BRS_T': getBot['BRS_T'],
            }
            jsonData(getBot['bot'], 'SET', botElements)
        klines = {}
        while operationLoop:
            try:
                klineConnect = True
                klineConnectCount = 0
                while klineConnect:
                    try:
                        klines = client.futures_klines(symbol=getBot['parity'], interval=str(getBot['time']), limit=int(getBot['BRS_LIMIT']))
                        klineConnect = False
                    except Exception as e:
                        klineConnectCount += 1
                        if ("Max retries exceeded" in str(e) or "Too many requests" in str(e) or "recvWindow" in str(e) or "Connection broken" in str(e) or "Please try again" in str(e)) and klineConnectCount < 3:
                            time.sleep(float(config('SETTING', 'TIME_SLEEP')))
                        elif "Way too many requests" in str(e) or "Read timed out." in str(e) or (3 <= klineConnectCount <= 6):
                            proxyOrder = requests.post(url + 'proxy-order/' + str(getBot['bot']), headers={
                                'neresi': 'dogunun+billurlari'
                            }).json()
                            client = Client(str(getBot['api_key']), str(getBot['api_secret']), {"timeout": 300, 'proxies': proxyOrder})
                        else:
                            raise Exception(e)
                getBRS = brs(klines, botElements['BRS_M'], botElements['BRS_T'])
                if getBRS['M'] != sameTest['M'] or getBRS['T'] != sameTest['T'] or getBRS['C'] != sameTest['C']:
                    botElements['BRS_M'] = getBRS['M']
                    botElements['BRS_T'] = getBRS['T']
                    sameTest = {
                        'M': getBRS['M'],
                        'T': getBRS['T'],
                        'C': getBRS['C']
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
                                'neresi': 'dogunun+billurlari'
                            }, json={
                                'line': getframeinfo(currentframe()).lineno,
                                'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                'BRS': getBRS['BRS'],
                                'BRS_M': getBRS['M'],
                                'BRS_T': getBRS['T'],
                                'BRS_C': getBRS['T'],
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
                        if botElements['lastSide'] != getBRS['side'] and botElements['orderStatus'] == False:
                            botElements['lastPrice'] = float(client.futures_ticker(symbol=getBot['parity'])['lastPrice'])
                            if botElements['lastSide'] != 'HOLD' and botElements['orderStatus'] == True:
                                positionConnect = True
                                positionConnectCount = 0
                                try:
                                    position = getPosition(client, getBot['parity'], botElements['lastType'])
                                    positionConnect = False
                                except Exception as e:
                                    positionConnectCount += 1
                                    if ("Max retries exceeded" in str(e) or "Too many requests" in str(e) or "recvWindow" in str(e) or "Connection broken" in str(e) or "Please try again" in str(e)) and positionConnectCount < 3:
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
                                    orderCreate = True
                                    orderCreateCount = 0
                                    while orderCreate:
                                        try:
                                            client.futures_create_order(symbol=getBot['parity'], side=getBRS['side'], positionSide=botElements['lastType'], type="MARKET", quantity=botElements['lastQuantity'])
                                            orderCreate = False
                                        except Exception as e:
                                            orderCreateCount += 1
                                            if ("Max retries exceeded" in str(e) or "Too many requests" in str(e) or "recvWindow" in str(e) or "Connection broken" in str(e) or "Please try again" in str(e)) and orderCreateCount < 3:
                                                time.sleep(float(config('SETTING', 'TIME_SLEEP')))
                                            elif "Way too many requests" in str(e) or "Read timed out." in str(e) or (3 <= orderCreateCount <= 6):
                                                proxyOrder = requests.post(url + 'proxy-order/' + str(getBot['bot']), headers={
                                                    'neresi': 'dogunun+billurlari'
                                                }).json()
                                                getBot['proxy'] = proxyOrder['proxy']
                                            else:
                                                raise Exception(e)

                                    # Binance END
                                    setBotWhile = True
                                    setBotCount = 0
                                    while setBotWhile:
                                        setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                                            'neresi': 'dogunun+billurlari'
                                        }, json={
                                            'line': getframeinfo(currentframe()).lineno,
                                            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                            'BRS': getBRS['BRS'],
                                            'BRS_M': getBRS['M'],
                                            'BRS_T': getBRS['T'],
                                            'BRS_C': getBRS['C'],
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
                                            'BRS': getBRS['BRS'],
                                            'BRS_M': getBRS['M'],
                                            'BRS_T': getBRS['T'],
                                            'BRS_C': getBRS['C'],
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
                                        'BRS': getBRS['BRS'],
                                        'BRS_M': getBRS['M'],
                                        'BRS_T': getBRS['T'],
                                        'BRS_C': getBRS['C'],
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
                                botElements['lastSide'] = getBRS['side']
                                botElements['lastType'] = getBRS['type']
                                botElements['firstLogin'] = False
                                # Binance
                                botElements['balance'] = getOrderBalance(client, "USDT", int(getBot['percent']))

                                # profit trigger
                                botElements['maxDamageUSDT'] = round((botElements['balance'] / 100) * int(getBot['MAX_DAMAGE_USDT_PERCENT']), 2)
                                botElements['maxDamageCount'] = 0
                                botElements['maxDamageBefore'] = 0
                                botElements['profitMax'] = profitMax(klines, int(getBot['leverage']))
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
                                        if ("Max retries exceeded" in str(e) or "Too many requests" in str(e) or "recvWindow" in str(e) or "Connection broken" in str(e) or "Please try again" in str(e)) and orderCreateCount < 3:
                                            time.sleep(float(config('SETTING', 'TIME_SLEEP')))
                                        elif "Way too many requests" in str(e) or "Read timed out." in str(e) or (3 <= orderCreateCount <= 6):
                                            proxyOrder = requests.post(url + 'proxy-order/' + str(getBot['bot']), headers={
                                                'neresi': 'dogunun+billurlari'
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
                                        'neresi': 'dogunun+billurlari'
                                    }, json={
                                        'line': getframeinfo(currentframe()).lineno,
                                        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        'BRS': getBRS['BRS'],
                                        'BRS_M': getBRS['M'],
                                        'BRS_T': getBRS['T'],
                                        'BRS_C': getBRS['C'],
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
                                        'BRS': getBRS['BRS'],
                                        'BRS_M': getBRS['M'],
                                        'BRS_T': getBRS['T'],
                                        'BRS_C': getBRS['C'],
                                        'action': 'ORDER_START_WAITING',
                                    })
                                    if setBot.status_code == 200:
                                        setBotWhile = False
                                    elif setBotCount >= int(config('API', 'ERR_COUNT')):
                                        raise Exception('server_error')
                                    else:
                                        time.sleep(1)
                                        setBotCount += 1
                            elif botElements['orderStatus']:
                                positionConnect = True
                                positionConnectCount = 0
                                try:
                                    position = getPosition(client, getBot['parity'], botElements['lastType'])
                                    positionConnect = False
                                except Exception as e:
                                    positionConnectCount += 1
                                    if ("Max retries exceeded" in str(e) or "Too many requests" in str(e) or "recvWindow" in str(e) or "Connection broken" in str(e) or "Please try again" in str(e)) and positionConnectCount < 3:
                                        time.sleep(float(config('SETTING', 'TIME_SLEEP')))
                                    elif "Way too many requests" in str(e) or "Read timed out." in str(e) or (3 <= positionConnectCount <= 6):
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
                                elif position['profit'] < 0:
                                    if abs(position['profit']) >= botElements['maxDamageUSDT']:
                                        if botElements['maxDamageBefore'] < abs(position['profit']):
                                            botElements['maxDamageCount'] += 1
                                            if botElements['maxDamageCount'] >= int(config('SETTING', 'MAX_DAMAGE_COUNT')):
                                                botElements['triggerKey'] = "MAX_DAMAGE"
                                                botElements['profitTurn'] = True
                                        else:
                                            botElements['maxDamageCount'] = 0
                                        botElements['maxDamageBefore'] = abs(position['profit'])
                                jsonData(getBot['bot'], 'SET', botElements)

                                if botElements['profitTurn']:
                                    botElements['profitTurn'] = False
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
                                            if ("Max retries exceeded" in str(e) or "Too many requests" in str(e) or "recvWindow" in str(e) or "Connection broken" in str(e) or "Please try again" in str(e)) and orderCreateCount < 3:
                                                time.sleep(float(config('SETTING', 'TIME_SLEEP')))
                                            elif "Way too many requests" in str(e) or "Read timed out." in str(e) or (3 <= orderCreateCount <= 6):
                                                proxyOrder = requests.post(url + 'proxy-order/' + str(getBot['bot']), headers={
                                                    'neresi': 'dogunun+billurlari'
                                                }).json()
                                                getBot['proxy'] = proxyOrder['proxy']
                                            else:
                                                raise Exception(e)

                                    setBotWhile = True
                                    setBotCount = 0
                                    while setBotWhile:
                                        setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                                            'neresi': 'dogunun+billurlari'
                                        }, json={
                                            'line': getframeinfo(currentframe()).lineno,
                                            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                            'BRS': getBRS['BRS'],
                                            'BRS_M': getBRS['M'],
                                            'BRS_T': getBRS['T'],
                                            'BRS_C': getBRS['C'],
                                            'side': botElements['lastSide'],
                                            'price': position['markPrice'],
                                            'profit': position['profit'],
                                            'quantity': position['amount'],
                                            'action': botElements['triggerKey'],
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
                                            'BRS': getBRS['BRS'],
                                            'BRS_M': getBRS['M'],
                                            'BRS_T': getBRS['T'],
                                            'BRS_C': getBRS['C'],
                                            'action': 'ORDER_ENDING_WAITING',
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
                    # Wait 3 minute
                    time.sleep(180)
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
        requests.post(url + 'delete-bots', headers={
            'neresi': 'dogunun+billurlari'
        })
        sys.exit(0)
