import requests

req = requests.post('http://127.0.0.1:8000/api/test', headers={
    'neresi': 'dogunun+billurlari'
}, json={
    'bot': "AAAA",
    'errors': [

    ]
}).text
print(req)
