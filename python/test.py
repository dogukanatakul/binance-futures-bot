import time

from binance.client import Client
from inspect import currentframe, getframeinfo

client = Client(str("SjlxXktwDHd1h7Nrg9HnAQM4oJ7R8tu9H7joAEJM9mPc79RWkj0qDMviby1wb7Zq"), str("KWyjvXX4lkMBtlwIj9R4BIJkpLgYcfwNfFIiSUemojroJaEgDLgGsnz7rfb4CHYG"))


# client.futures_income_history(symbol=symbol, limit=4)


def endPositionCheck(symbol):
    try:
        positions = client.futures_account_trades(symbol=symbol, limit=2)
        if len(positions) > 0:
            position = positions[-2]
            if (position['positionSide'] == 'LONG' and position['side'] == 'SELL') or (position['positionSide'] == 'SHORT' and position['side'] == 'BUY'):
                return {
                    'status': 'success',
                    'profit': position['realizedPnl'],
                    'price': position['price'],
                    'balance': position['quoteQty'],
                    'line': getframeinfo(currentframe()).lineno,
                }
            else:
                return {
                    'status': 'continue',
                }
        else:
            return {
                'status': 'no_data',
            }
    except:
        return {
            'status': 'fail',
        }


print(endPositionCheck('AAVEUSDT'))
