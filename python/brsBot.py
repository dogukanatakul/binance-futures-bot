#!/usr/bin/python3
import time, sys, os, requests, uuid
from datetime import datetime
from binance.client import Client
import json
from helper import config
from inspect import currentframe, getframeinfo
import logging

url = config('API', 'SITE')


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
            'fee': round(((abs(float(info['positionAmt'])) * 15) / 1000) * 0.0400, 2),
            'leverage': int(info['leverage'])
        }
    return positions[side]


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


def brs(bot):
    try:
        if os.path.exists(os.path.dirname(os.path.realpath(__file__)) + "/syncs/" + bot + '.json'):
            return json.loads(open(os.path.dirname(os.path.realpath(__file__)) + "/syncs/" + bot + '.json', "r").read())
        else:
            return False
    except:
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
        if getBot['status'] == 'fail':
            os.execl(sys.executable, sys.executable, *sys.argv)
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
                logging.error(str(e))
                clientConnectCount += 1
                if ("Max retries exceeded" in str(e) or "Too many requests" in str(e) or "recvWindow" in str(e) or "Connection broken" in str(e) or "Please try again" in str(e)) and clientConnectCount < 3:
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
        priceFractions = {}
        for item in info['symbols']:
            fractions[item['symbol']] = item['quantityPrecision']
            priceFractions[item['symbol']] = item['pricePrecision']
        # LONG: BUY | SHORT: SELL
        sameTest = {
            'BRS': 0,
        }
        operationLoop = True

        # ilerleme yapısı
        if len(getBot['transfer']) > 0:
            transferFailStatus = True
            for transferUuid in getBot['transfer']:
                botElements = jsonData(transferUuid, 'GET')
                if botElements:
                    jsonData(getBot['bot'], 'SET', botElements)
                    jsonData(getBot['transfer'][0], 'DELETE')
                    transferFailStatus = False
                    break
            if transferFailStatus:
                errBotWhile = True
                errBotCount = 0
                while errBotWhile:
                    errBot = requests.post(url + 'set-error', headers={
                        'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                    }, json={
                        'bot': getBot['bot'],
                        'errors': [
                            "ilerleme dosyasi bulunamadi.",
                            getBot['transfer'][0],
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
                os.execl(sys.executable, sys.executable, *sys.argv)
        else:
            botElements = {
                'lastPrice': 0,
                'lastSide': 'HOLD',
                'lastType': None,
                'orderStatus': False,
                'profitTurn': False,
                'triggerKey': None,
                'lastQuantity': None,
                'newTriggerOrder': False,
                'balance': 0,
                'stopLoss': 0,
            }
            jsonData(getBot['bot'], 'SET', botElements)
        # ilerleme yapısı

        getBRS = {
            'BRS': 0
        }
        while operationLoop:
            try:
                brsConnect = True
                brsConnectCount = 0
                while brsConnect:
                    try:
                        getBRS = brs(getBot['parity'])
                        if not getBRS:
                            # dosya çekilemediyse
                            raise Exception("dont_get_file")
                        brsConnect = False
                    except Exception as e:
                        logging.error(str(e))
                        brsConnectCount += 1
                        if brsConnectCount > int(config('API', 'ERR_COUNT_BRS')):
                            raise Exception(e)
                        else:
                            time.sleep(float(config('SETTING', 'TIME_SLEEP')))
                if getBRS['BRS'] != sameTest['BRS']:
                    sameTest = {
                        'BRS': getBRS['BRS'],
                    }
                    # SYNC BOT
                    syncBotWhile = True
                    syncBotCount = 0
                    while syncBotWhile:
                        syncBot = requests.post(url + 'get-order/' + getBot['bot'], headers={
                            'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                        })
                        if syncBot.status_code == 200:
                            if syncBot.json()['status'] == 0:
                                os.execl(sys.executable, sys.executable, *sys.argv)
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
                        if botElements['lastSide'] != getBRS['side']:
                            botElements['lastPrice'] = float(client.futures_ticker(symbol=getBot['parity'])['lastPrice'])
                            if botElements['lastSide'] != 'HOLD' and botElements['orderStatus'] == True:
                                positionConnect = True
                                positionConnectCount = 0
                                position = {}
                                try:
                                    position = getPosition(client, getBot['parity'], botElements['lastType'])
                                    positionConnect = False
                                except Exception as e:
                                    logging.error(str(e))
                                    positionConnectCount += 1
                                    if ("Max retries exceeded" in str(e) or "Too many requests" in str(e) or "recvWindow" in str(e) or "Connection broken" in str(e) or "Please try again" in str(e)) and positionConnectCount < 3:
                                        time.sleep(float(config('SETTING', 'TIME_SLEEP')))
                                    elif "Way too many requests" in str(e) or "Read timed out." in str(e) or (3 <= positionConnectCount <= 6):
                                        proxyOrder = requests.post(url + 'proxy-order/' + str(getBot['bot']), headers={
                                            'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                                        }).json()
                                        getBot['proxy'] = proxyOrder['proxy']
                                        client = Client(str(getBot['api_key']), str(getBot['api_secret']), {"timeout": 40, 'proxies': getBot['proxy']})
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
                                            logging.error(str(e))
                                            orderCreateCount += 1
                                            if ("Max retries exceeded" in str(e) or "Too many requests" in str(e) or "recvWindow" in str(e) or "Connection broken" in str(e) or "Please try again" in str(e)) and orderCreateCount < 3:
                                                time.sleep(float(config('SETTING', 'TIME_SLEEP')))
                                            elif "Way too many requests" in str(e) or "Read timed out." in str(e) or (3 <= orderCreateCount <= 6):
                                                proxyOrder = requests.post(url + 'proxy-order/' + str(getBot['bot']), headers={
                                                    'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                                                }).json()
                                                getBot['proxy'] = proxyOrder['proxy']
                                                client = Client(str(getBot['api_key']), str(getBot['api_secret']), {"timeout": 40, 'proxies': getBot['proxy']})
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
                                            'side': botElements['lastSide'],
                                            'action': 'MANUAL_STOP_OR_MAX_DAMAGE',
                                        })
                                        if setBot.status_code == 200:
                                            setBotWhile = False
                                        elif setBotCount >= int(config('API', 'ERR_COUNT')):
                                            raise Exception('server_error')
                                        else:
                                            time.sleep(1)
                                            setBotCount += 1
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
                                # Binance
                                botElements['balance'] = getOrderBalance(client, "USDT", int(getBot['percent']))

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
                                        logging.error(str(e))
                                        orderCreateCount += 1
                                        if ("Max retries exceeded" in str(e) or "Too many requests" in str(e) or "recvWindow" in str(e) or "Connection broken" in str(e) or "Please try again" in str(e)) and orderCreateCount < 3:
                                            time.sleep(float(config('SETTING', 'TIME_SLEEP')))
                                        elif "Way too many requests" in str(e) or "Read timed out." in str(e) or (3 <= orderCreateCount <= 6):
                                            proxyOrder = requests.post(url + 'proxy-order/' + str(getBot['bot']), headers={
                                                'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                                            }).json()
                                            getBot['proxy'] = proxyOrder['proxy']
                                            client = Client(str(getBot['api_key']), str(getBot['api_secret']), {"timeout": 40, 'proxies': getBot['proxy']})
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
                                position = {}
                                positionConnect = True
                                positionConnectCount = 0
                                try:
                                    position = getPosition(client, getBot['parity'], botElements['lastType'])
                                    positionConnect = False
                                except Exception as e:
                                    logging.error(str(e))
                                    positionConnectCount += 1
                                    if ("Max retries exceeded" in str(e) or "Too many requests" in str(e) or "recvWindow" in str(e) or "Connection broken" in str(e) or "Please try again" in str(e)) and positionConnectCount < 3:
                                        time.sleep(float(config('SETTING', 'TIME_SLEEP')))
                                    elif "Way too many requests" in str(e) or "Read timed out." in str(e) or (3 <= positionConnectCount <= 6):
                                        proxyOrder = requests.post(url + 'proxy-order/' + str(getBot['bot']), headers={
                                            'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                                        }).json()
                                        client = Client(str(getBot['api_key']), str(getBot['api_secret']), {"timeout": 40, 'proxies': proxyOrder})
                                    else:
                                        raise Exception(e)

                                if position['amount'] <= 0:
                                    raise Exception('close')
                                jsonData(getBot['bot'], 'SET', botElements)
                                setBotWhile = True
                                setBotCount = 0
                                while setBotWhile:
                                    setBot = requests.post(url + 'set-order/' + str(getBot['bot']), headers={
                                        'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                                    }, json={
                                        'line': getframeinfo(currentframe()).lineno,
                                        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
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
                    time.sleep(1)
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
                    os.execl(sys.executable, sys.executable, *sys.argv)
            except KeyboardInterrupt:
                requests.post(url + 'delete-bots', headers={
                    'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                })
                os.execl(sys.executable, sys.executable, *sys.argv)
    except Exception as exception:
        logging.error(str(exception))
        requests.post(url + 'delete-bots', headers={
            'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
        })
        os.execl(sys.executable, sys.executable, *sys.argv)
