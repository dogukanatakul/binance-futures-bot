import random, time, sys, os, requests, uuid
from datetime import datetime
from binance.client import Client
import pandas as pd
import termtables as tt
from helper import config
from inspect import currentframe, getframeinfo

url = config('API', 'SITE')


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


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
    return df.tail(1)['K'].item(), df.tail(1)['D'].item(), df.tail(1)['J'].item()


def get_kdj(klines, period=9, signal=2):
    try:
        k, d, j = kdj(klines, period, signal)
        if float(j) > float(d) and float(d) < float(k):
            return {
                'K': k,
                'D': d,
                'J': j,
                'type': 'LONG',
                'side': 'BUY'
            }
        else:
            return {
                'K': k,
                'D': d,
                'J': j,
                'type': 'SHORT',
                'side': 'SELL'
            }
    except Exception as e:
        return False


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


def getPosition(client, symbol, side):
    infos = client.futures_position_information(symbol=symbol)
    positions = {}
    for info in infos:
        positions[info['positionSide']] = {
            'amount': abs(float(info['positionAmt'])),
            'entryPrice': float(info['entryPrice']),
            'markPrice': float(info['markPrice']),
            'profit': float(info['unRealizedProfit']),
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


getBot = {
    'status': 0
}
version = None
while True:
    botUuid = str(uuid.uuid4())
    while getBot['status'] == 0 or getBot['status'] == 2:
        time.sleep(random.randint(2, 5))
        getBot = requests.post(url + 'get-order/' + botUuid, headers={
            'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
        }).json()
        if version is not None and getBot['status'] == 0 and getBot['version'] != version:
            os.execl(sys.executable, sys.executable, *sys.argv)
        else:
            version = getBot['version']

    client = Client(str(getBot['api_key']), str(getBot['api_secret']), {"timeout": 300, 'proxies': getBot['proxy']})

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
    lastQuantity = None
    triggerStatus = False
    profitTrigger = False
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
            while klineConnect:
                try:
                    klines = client.futures_klines(symbol=getBot['parity'], interval=minutes[str(getBot['time'])], limit=100)
                    suKlines = client.futures_klines(symbol=getBot['parity'], interval=minutes[str(getBot['sub_time'])], limit=100)
                    klineConnect = False
                except Exception as e:
                    if "Max retries exceeded" in str(e) or "Too many requests" in str(e) or "recvWindow" in str(e):
                        time.sleep(1)
                    elif "Way too many requests" in str(e) or "Read timed out." in str(e):
                        proxyOrder = requests.post(url + 'proxy-order/' + str(getBot['bot']), headers={
                            'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                        }).json()
                        client = Client(str(getBot['api_key']), str(getBot['api_secret']), {"timeout": 300, 'proxies': proxyOrder})
                    else:
                        raise Exception(e)
            getKDJ = get_kdj(klines, getBot['kdj_period'], getBot['kdj_signal'])
            getSubKDJ = get_kdj(suKlines, getBot['sub_kdj_period'], getBot['sub_kdj_signal'])
            if getKDJ['K'] != sameTest['K'] or getKDJ['D'] != sameTest['D'] or getKDJ['J'] != sameTest['J']:
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
                        'K': getKDJ['K'],
                        'D': getKDJ['D'],
                        'J': getKDJ['J'],
                        'action': 'STOP',
                    }).status_code
                    if setBot != 200:
                        raise Exception('set_bot_fail')
                    raise Exception('STOP')
                else:
                    if lastSide != getKDJ['side'] and getKDJ['side'] == getSubKDJ['side']:
                        lastPrice = float(client.futures_ticker(symbol=getBot['parity'])['lastPrice'])
                        if lastSide != 'HOLD' and profitTrigger == False:
                            position = getPosition(client, getBot['parity'], lastType)
                            if position['amount'] > 0:
                                # Binance
                                client.futures_create_order(symbol=getBot['parity'], side=getKDJ['side'], positionSide=lastType, type="MARKET", quantity=lastQuantity)
                                # Binance END
                                setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                                    'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                                }, json={
                                    'line': getframeinfo(currentframe()).lineno,
                                    'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    'K': getKDJ['K'],
                                    'D': getKDJ['D'],
                                    'J': getKDJ['J'],
                                    'side': lastSide,
                                    'price': lastPrice,
                                    'profit': position['profit'],
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
                                    'K': getKDJ['K'],
                                    'D': getKDJ['D'],
                                    'J': getKDJ['J'],
                                    'side': lastSide,
                                    'action': 'MANUAL_STOP',
                                }).status_code
                                raise Exception('manual_stop')
                        else:
                            triggerStatus = False
                            profitTrigger = False

                        lastSide = getKDJ['side']
                        lastType = getKDJ['type']

                        # Binance
                        balance = getOrderBalance(client, "USDT", int(getBot['percent']))
                        lastQuantity = "{:0.0{}f}".format(float((balance / lastPrice) * getBot['leverage']), fractions[getBot['parity']])
                        if float(lastQuantity) <= 0:
                            raise Exception("Bakiye hatası")
                        client.futures_create_order(symbol=getBot['parity'], side=lastSide, type='MARKET', quantity=lastQuantity, positionSide=lastType)
                        # Binance END

                        setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                            'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                        }, json={
                            'line': getframeinfo(currentframe()).lineno,
                            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'K': getKDJ['K'],
                            'D': getKDJ['D'],
                            'J': getKDJ['J'],
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
                        if lastPrice == 0:
                            setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                                'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                            }, json={
                                'line': getframeinfo(currentframe()).lineno,
                                'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                'K': getKDJ['K'],
                                'D': getKDJ['D'],
                                'J': getKDJ['J'],
                                'action': 'ORDER_START_WAITING',
                            }).status_code
                            if setBot != 200:
                                raise Exception('set_bot_fail')
                        elif getBot['profit'] > 0 and lastPrice != 0 and profitTrigger == False:
                            # get Position
                            positionConnect = True
                            try:
                                position = getPosition(client, getBot['parity'], lastType)
                                positionConnect = False
                            except Exception as e:
                                if "Max retries exceeded" in str(e) or "Too many requests" in str(e) or "recvWindow" in str(e):
                                    time.sleep(1)
                                elif "Way too many requests" in str(e) or "Read timed out." in str(e):
                                    proxyOrder = requests.post(url + 'proxy-order/' + str(getBot['bot']), headers={
                                        'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                                    }).json()
                                    client = Client(str(getBot['api_key']), str(getBot['api_secret']), {"timeout": 40, 'proxies': proxyOrder})
                                else:
                                    raise Exception(e)
                            if position['profit'] > getBot['profit']:
                                profitTrigger = True
                                triggerStatus = True
                                client.futures_create_order(symbol=getBot['parity'], side='SELL' if lastType == 'LONG' else "BUY", positionSide=lastType, type="MARKET", quantity=lastQuantity)
                                setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                                    'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                                }, json={
                                    'line': getframeinfo(currentframe()).lineno,
                                    'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    'K': getKDJ['K'],
                                    'D': getKDJ['D'],
                                    'J': getKDJ['J'],
                                    'side': lastSide,
                                    'profit': position['profit'],
                                    'action': 'PROFIT_TRIGGER',
                                }).status_code
                                if setBot != 200:
                                    raise Exception('set_bot_fail')
                                # get Position END
                # Max Request Sleep
                if getBot['time'] == '30min':
                    time.sleep(3)
                elif getBot['time'] == '1hour':
                    time.sleep(3)
                elif getBot['time'] == '4hour':
                    time.sleep(3)
                else:
                    time.sleep(3)
                # Max Request Sleep
            else:
                if getBot['time'] == '30min':
                    time.sleep(3)
                elif getBot['time'] == '1hour':
                    time.sleep(3)
                elif getBot['time'] == '4hour':
                    time.sleep(3)
                else:
                    time.sleep(3)
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
