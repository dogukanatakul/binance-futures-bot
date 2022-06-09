from binance.client import Client
import pandas as pd
import logging

logging.basicConfig(filename='datas/example.log', level=logging.DEBUG)

try:
    raise Exception("dsadas")
except Exception as exception:
    logging.error(str(exception))
