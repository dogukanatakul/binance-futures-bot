from binance.client import Client

client = Client(str("dVLkUfHkVax8GHy9DLKf3DTOaI2Tkw1iBy1I9bEtC6bwCTXCRiZzeTYquuOA6oby"), str("x6QqRCYtyN3LaejTrLKxirVnepswEmfBKFhG5ckCG9NZuIYHRQs3bvy3I1nI3rvG"), {"timeout": 300})
print(client.futures_position_information(symbol="ETCUSDT"))
