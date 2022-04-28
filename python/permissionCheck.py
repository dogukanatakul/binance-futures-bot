import time
from binance.client import Client
from helper import config
import requests

while True:
    users = requests.post(config('API', 'SITE') + 'get-req-user', headers={
        'neresi': 'dogunun+billurlari'
    }).json()
    for user in users:
        permissions = [
            'enableReading',
            'enableFutures',  # Vadeli işlem hesabınız açılmadan önce oluşturulan API Anahtarı, vadeli işlem API hizmetini desteklemiyor
        ]
        try:
            client = Client(user['api_key'], user['api_secret'], {"timeout": 40})
            get_account_api_permissions = client.get_account_api_permissions()
            client.futures_get_position_mode()
            for attr, value in get_account_api_permissions.items():
                if attr in permissions and value:
                    permissions.remove(attr)
            print(permissions)
            setPerm = requests.post(config('API', 'SITE') + 'set-req-user', headers={
                'neresi': 'dogunun+billurlari'
            }, json={
                'user': user['id'],
                'permissions': permissions
            }).json()
        except Exception as e:
            print(str(e))
            if str(e).find("Invalid API-key") >= 0:
                setPerm = requests.post(config('API', 'SITE') + 'set-req-user', headers={
                    'neresi': 'dogunun+billurlari'
                }, json={
                    'user': user['id'],
                    'status': 'fail'
                }).json()
    time.sleep(5)
