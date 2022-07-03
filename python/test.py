import time, datetime, os, json
import pandas as pd
from binance.client import Client


def microTime(dt):
    return datetime.datetime.fromtimestamp(dt / 1000.0).strftime("%Y-%m-%d %H:%M:%S")


print(microTime(1656775080000))
