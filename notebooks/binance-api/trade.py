import json
import websocket
import pandas as pd

symbol = 'btcusdt'
socket = f'wss://stream.binance.com:9443/ws/{symbol}@trade'

def on_message(ws, message):
    print(message)

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    print("Opened connection")

ws = websocket.WebSocketApp(socket,
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)

ws.run_forever()