from binance.client import Client

client = Client("l8FqzEGOW91yP139vjZKDMs6oZJse4Isl3emol6dAMwVwKhHvOwH5irOVBvBhsVc", "eMlTWnJKQypSF2nlpCoWqTv6zyXej2hjDt2e7iqTNQbMoRQW3mOp94bkowj1OAtg", {"timeout": 40})

dual = client.futures_get_position_mode()
if not dual['dualSidePosition']:
    client.futures_change_position_mode(dualSidePosition=True)
print(client.futures_change_leverage(symbol="DOGEUSDT", leverage=10))



