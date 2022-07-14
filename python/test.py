from binance.client import Client
from inspect import currentframe, getframeinfo

client = Client(str("giu0GTye78gpNyJlc1HwdP2NBWSYHr6L6scrsDjaZbQTGpFtoG6NBhkrY9w2a1SN"), str("ZiYBB0p5HLO3HA1P5dp6V9kBTRddWlGw6n2H0phEUHk60EBVn1Q6TRDLtHHdCDMp"))


def endPositionCheck(symbol):
    try:
        positions = client.futures_get_all_orders(symbol=symbol, limit=1)
        if len(positions) > 0:
            position = positions[-1]
            if (position['positionSide'] == 'LONG' and position['side'] == 'SELL') or (position['positionSide'] == 'SHORT' and position['side'] == 'BUY'):
                return {
                    'status': 'success',
                    'line': getframeinfo(currentframe()).lineno,
                }
        else:
            return {
                'status': 'fail',
            }
    except:
        return {
            'status': 'fail',
        }


print(endPositionCheck('AAVEUSDT'))
