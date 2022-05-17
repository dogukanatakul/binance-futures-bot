from binance.client import Client


def getPosition(client, symbol, side):
    infos = client.futures_position_information(symbol=symbol)
    print(infos)
    positions = {}
    for info in infos:
        positions[info['positionSide']] = {
            'amount': abs(float(info['positionAmt'])),
            'entryPrice': float(info['entryPrice']),
            'markPrice': float(info['markPrice']),
            'profit': float(info['unRealizedProfit']),
        }
    return positions[side]


client = Client(str("l8FqzEGOW91yP139vjZKDMs6oZJse4Isl3emol6dAMwVwKhHvOwH5irOVBvBhsVc"), str("eMlTWnJKQypSF2nlpCoWqTv6zyXej2hjDt2e7iqTNQbMoRQW3mOp94bkowj1OAtg"))

print(getPosition(client, "DOGEUSDT", "SHORT"))
