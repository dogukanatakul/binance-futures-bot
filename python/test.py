from binance.client import Client

client = Client("SjlxXktwDHd1h7Nrg9HnAQM4oJ7R8tu9H7joAEJM9mPc79RWkj0qDMviby1wb7Zq", "KWyjvXX4lkMBtlwIj9R4BIJkpLgYcfwNfFIiSUemojroJaEgDLgGsnz7rfb4CHYG", {"timeout": 40})


def getPosition(client, symbol, side):
    info = client.futures_position_information(symbol=str(symbol))
    positions = {}
    for item in info:
        positions[item['positionSide']] = {
            'amount': float(item['positionAmt']),
            'entryPrice': float(item['entryPrice']),
            'markPrice': float(item['markPrice']),
            'profit': float(item['unRealizedProfit']),
        }
    return positions[side]


print(getPosition(client, 'DOGEUSDT', "SHORT"))
