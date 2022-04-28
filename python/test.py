from binance import ThreadedWebsocketManager
from binance.client import AsyncClient

twm = ThreadedWebsocketManager(api_key="l8FqzEGOW91yP139vjZKDMs6oZJse4Isl3emol6dAMwVwKhHvOwH5irOVBvBhsVc", api_secret="eMlTWnJKQypSF2nlpCoWqTv6zyXej2hjDt2e7iqTNQbMoRQW3mOp94bkowj1OAtg")
twm.start()


def handle_socket_message(msg):
    print(msg['s'], msg['k']['i'], msg)


twm.start_kline_socket(callback=handle_socket_message, symbol="DOGEUSDT", interval=AsyncClient.KLINE_INTERVAL_1MINUTE)

twm.stop()
