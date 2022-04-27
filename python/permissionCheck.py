import time
from binance.client import Client
from helper import config
import requests

while True:
    users = requests.post(config('API', 'SITE') + 'get-req-user', headers={
        'neresi': 'dogunun+billurlari'
    }).json()
    print(users)
    for user in users:
        permissions = [
            'enableReading',
            'enableFutures',  # Vadeli işlem hesabınız açılmadan önce oluşturulan API Anahtarı, vadeli işlem API hizmetini desteklemiyor
        ]
        try:
            get_account_api_permissions = client.get_account_api_permissions()
            client = Client(user['api_key'], user['api_secret'], {"timeout": 40})
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
            if str(e).find("Invalid Api-Key ID"):
                setPerm = requests.post(config('API', 'SITE') + 'set-req-user', headers={
                    'neresi': 'dogunun+billurlari'
                }, json={
                    'user': user['id'],
                    'status': 'fail'
                }).json()
    time.sleep(5)
