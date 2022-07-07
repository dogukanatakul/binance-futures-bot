sudo nano /etc/nginx/nginx.conf

```
server {
        listen [::]:443 http2;
        listen 443 http2;
        listen 80;
        listen PYTHON_PORT;
        server_name  DOMAIN.COM;
     
        # note that these lines are originally from the "location /" block
        root   /var/www/binance-futures-bot/public;
        index index.php index.html index.htm;

        
        add_header X-XSS-Protection "1; mode=block";
        add_header X-Frame-Options "SAMEORIGIN";
        add_header X-Content-Type-Options nosniff;
        add_header Referrer-Policy "strict-origin";
        add_header Permissions-Policy "geolocation=(),midi=(),sync-xhr=(),microphone=(),camera=(),magnetometer=(),gyroscope=(),fullscreen=(self),payment=()";
     
        location / {
            try_files $uri $uri/ /index.php?$query_string;
            proxy_set_header 'Access-Control-Allow-Origin' 'https://DOMAIN.COM';
        }
        error_page 404 /404.html;
        error_page 500 502 503 504 /50x.html;
        location = /50x.html {
            root /usr/share/nginx/html;
        }
     
        location ~ \.php$ {
            try_files $uri =404;
            fastcgi_pass unix:/run/php/php8.1-fpm.sock;
            fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;
        include fastcgi_params;
        }
     
        location ~* ^.+.(gif|ico|jpg|jpeg|png|flv|swf|pdf|mp3|mp4|xml|txt|js|css)$ {
            expires 30d;
            add_header Vary Accept-Encoding;
        }
}
```

```
sudo ufw allow PYTHON_PORT
```

### Açıklama

Belirlenen python portu python klasörü içerisindeki config.ini dosyasındaki http://127.0.0.1:PYTHON_PORT/api/ alanını etkiler.
