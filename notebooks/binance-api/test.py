# import json
# import websocket
# import pandas as pd
# from datetime import datetime

# symbol = 'btcusdt'
# socket = f'wss://stream.binance.com:9443/ws/{symbol}@kline_1m'

# t, o, h, l, c, v = [], [], [], [], [],  []

# def on_message(ws, message):
#     msg = json.loads(message)
#     bar = msg['k']
#     if bar['x'] == False:
#         t.append(bar['t'])
#         o.append(bar['o'])
#         h.append(bar['h'])
#         l.append(bar['l'])
#         c.append(bar['c'])
#         v.append(bar['v'])
    
#     tt = bar['t']
#     print(tt)
#     print(datetime.fromtimestamp(tt/1000))
#     # print(f"Time: {bar['t']}, Open: {bar['o']}, High: {bar['h']}, Low: {bar['l']}, Close: {bar['c']}, Volume: {bar['v']}")
        
# def on_error(ws, error):
#     print(error)

# def on_close(ws, close_status_code, close_msg):
#     print("### closed ###")


# def on_open(ws):
#     print("Opened connection")

# ws = websocket.WebSocketApp(
#     socket,
#     on_open=on_open,
#     on_message=on_message,
#     on_error=on_error,
#     on_close=on_close
# )

# ws.run_forever()


import requests
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import os

from dotenv import load_dotenv
load_dotenv()

api_key = os.environ['BINANCE_API_KEY_TEST']
api_secret = os.environ['BINANCE_API_SECRET_TEST']

url = 'https://api1.binance.com'

from binance.client import Client

client = Client(api_key, api_secret)

from binance import BinanceSocketManager
bsm = BinanceSocketManager(client)
socket = bsm.trade_socket('BTCBUSD')
