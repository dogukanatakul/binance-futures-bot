from binance.client import Client

client = Client("dVLkUfHkVax8GHy9DLKf3DTOaI2Tkw1iBy1I9bEtC6bwCTXCRiZzeTYquuOA6oby", "x6QqRCYtyN3LaejTrLKxirVnepswEmfBKFhG5ckCG9NZuIYHRQs3bvy3I1nI3rvG", {"timeout": 40})


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


# client.futures_create_order(symbol="XRPUSDT", side="BUY", positionSide="SHORT", type="MARKET", quantity=173.5)

print(getPosition(client, "XRPUSDT", "SHORT"))
