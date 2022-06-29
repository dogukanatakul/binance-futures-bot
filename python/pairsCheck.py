import time

from binance.client import Client
from helper import config
import requests

client = Client()
while True:
    for item in client.futures_exchange_info()['symbols']:
        if 'USDT' in item['pair']:
            setPair = requests.post(config('API', 'SITE') + 'update-parity', headers={
                'neresi': 'dogunun+billurlari'
            }, json={
                'min_price': item['filters'][0]['minPrice'],
                'max_price': item['filters'][0]['maxPrice'],
                'max_amount': item['filters'][1]['maxQty'],
                'min_amount': item['filters'][1]['minQty'],
                'price_fraction': item['pricePrecision'],
                'amount_fraction': item['quantityPrecision'],
                'binance_status': item['status'],
                'parity': item['symbol'],
            }).json()
            time.sleep(1)
