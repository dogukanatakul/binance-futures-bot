from binance.client import Client


def getPosition(client, symbol, side):
    try:
        infos = client.futures_position_information(symbol=symbol)
        positions = {}
        for info in infos:
            positions[info['positionSide']] = {
                'status': 'success',
                'amount': abs(float(info['positionAmt'])),
                'entryPrice': float(info['entryPrice']),
                'markPrice': float(info['markPrice']),
                'profit': float(info['unRealizedProfit']),
                'fee': round(((abs(float(info['positionAmt'])) * 15) / 1000) * 0.0400, 2),
                'leverage': int(info['leverage'])
            }
        if side in positions.keys() and 'amount' in positions[side].keys():
            return positions[side]
        else:
            return {
                'status': 'fail',
                'message': ''
            }
    except Exception as e:
        return {
            'status': 'fail',
            'message': str(e)
        }


client = Client(str("giu0GTye78gpNyJlc1HwdP2NBWSYHr6L6scrsDjaZbQTGpFtoG6NBhkrY9w2a1SN"), str("ZiYBB0p5HLO3HA1P5dp6V9kBTRddWlGw6n2H0phEUHk60EBVn1Q6TRDLtHHdCDMp"))
print(getPosition(client, 'XRPUSDT', 'LONG'))
