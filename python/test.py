import time
import pandas as pd
from datetime import timedelta, datetime
from binance.client import Client


def ceil_date(date, **kwargs):
    date = datetime.fromtimestamp(date / 1000.0).timestamp()
    secs = timedelta(**kwargs).total_seconds()
    return datetime.fromtimestamp(date + secs - date % secs).strftime("%d%H%M")


aa = 100
print(aa - (2 * 1.01))

#
client = Client("SjlxXktwDHd1h7Nrg9HnAQM4oJ7R8tu9H7joAEJM9mPc79RWkj0qDMviby1wb7Zq", "KWyjvXX4lkMBtlwIj9R4BIJkpLgYcfwNfFIiSUemojroJaEgDLgGsnz7rfb4CHYG")
# client.futures_create_order(symbol="1000SHIBUSDT", side="BUY", type='MARKET', quantity=500, positionSide="LONG")
# client.futures_create_order(symbol="1000SHIBUSDT", side="SELL", type='STOP_MARKET', quantity=500, positionSide="LONG", stopPrice=0.0103, closePosition="true")
# openOrdersF = client.futures_get_open_orders()
# if len(openOrdersF) > 0:
#     for orderF in openOrdersF:
#         client.futures_cancel_order(symbol="1000SHIBUSDT", orderId=orderF['orderId'])
#     print(openOrdersF)
# print("ok")
#
# print(client.futures_exchange_info())
