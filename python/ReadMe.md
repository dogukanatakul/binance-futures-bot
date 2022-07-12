# Requirements

```
#!/usr/bin/env bash
sudo apt install build-essential wget -y
wget https://artiya4u.keybase.pub/TA-lib/ta-lib-0.4.0-src.tar.gz
tar -xvf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
```

```
sudo pip install -r requirements.txt
```

```
sudo nano /etc/supervisor/supervisord.conf
sudo systemctl stop supervisor
sudo systemctl restart supervisor
```

### Config INI
```
[API]
SITE = http://SITE_URL/api/
ERR_COUNT = 4
ERR_COUNT_BRS = 10
[SETTING]
MAX_DAMAGE_COUNT = 1
TIME_SLEEP = 1
```
