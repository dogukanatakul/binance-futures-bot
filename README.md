### Kullanıcı Durumları

0. Yeni Üye
1. Binance Girişlerini Yapmış
2. Yönetici Tarafından Onaylanmış

### API Durumları

0. Girişler yapılmamış veya başarısız
1. Girişler yapılmış ve onaylı

### Emir Durumları

0. Botu Bekliyor
1. İşlemde
2. Durdurma Emri Verilmiş
3. Durmuş


### Zorunlu İşlemler
sudo chmod -R 777 /var/www/binance-futures-bot/storage/logs/


## Sembol Link Oluşturma
###  Linux Server:
ln -s /var/www/binance-futures-bot/storage/app/export /var/www/binance-futures-bot/public/export
### Windows Server
mklink /J C:\www\binance-futures-bot\storage\app\export C:\www\binance-futures-bot\public\export
