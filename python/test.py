from binance.client import Client
import pandas as pd
import logging
import time, sys, os, requests, uuid, talib, numpy


logging.basicConfig(filename=os.path.dirname(os.path.realpath(__file__))+'/datas/example.log', level=logging.DEBUG)

try:
    raise Exception("dsadas")
except Exception as exception:
    logging.error(str(exception))
