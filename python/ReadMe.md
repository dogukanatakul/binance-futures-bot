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


```
sudo ufw allow 1625
sudo nano /etc/nginx/nginx.conf
```



