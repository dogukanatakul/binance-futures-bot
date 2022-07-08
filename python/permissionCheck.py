import time
from binance.client import Client
from helper import config
import requests

while True:
    reqs = requests.post(config('API', 'SITE') + 'get-req-user', headers={
        'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
    }).json()
    proxyCount = 0
    for user in reqs['users']:
        permissions = [
            'enableReading',
            'enableFutures',  # Vadeli işlem hesabınız açılmadan önce oluşturulan API Anahtarı, vadeli işlem API hizmetini desteklemiyor
        ]
        try:
            client = Client(user['api_key'], user['api_secret'], {"timeout": 40, 'proxies': reqs['proxies'][proxyCount]})
            proxyCount += 1
            get_account_api_permissions = client.get_account_api_permissions()
            client.futures_get_position_mode()
            for attr, value in get_account_api_permissions.items():
                if attr in permissions and value:
                    permissions.remove(attr)
            setPerm = requests.post(config('API', 'SITE') + 'set-req-user', headers={
                'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
            }, json={
                'user': user['id'],
                'permissions': permissions
            }).json()
        except Exception as e:
            print(str(e))
            if str(e).find("Invalid API-key") >= 0:
                # APIError(code=-2008): Invalid Api-Key ID.
                setPerm = requests.post(config('API', 'SITE') + 'set-req-user', headers={
                    'rndUuid': '794d6f4b-f875-4ad1-aafa-b2e77a04bf58'
                }, json={
                    'user': user['id'],
                    'status': 'fail'
                }).json()
        time.sleep(1)
    time.sleep(2)
