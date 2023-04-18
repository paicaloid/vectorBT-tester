import os
import vectorbtpro as vbt
from binance.client import Client
from datetime import datetime, timedelta
import numpy as np

import pytz

import json
import websocket
import pandas as pd
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

from indicators.adx import ADX

symbol = 'btcusdt'
socket = f'wss://stream.binance.com:9443/ws/{symbol}@kline_1m'

tz = pytz.timezone('Asia/Bangkok')

class ADX_strategy:
    
    def __init__(self):
        self.symbol = "BTCUSDT"
        self.tz_str = "Asia/Bangkok"
        self.tz = pytz.timezone(self.tz_str)
        self.timeframe = "1 minutes"
        self.bar_range = 250
        self.tolerance = timedelta(milliseconds=1)
        
        self.adx_level = 25
        self.orders = []
        self.list_of_orders = []
        self.position = 0
    
    def on_message(self, ws, message):
        msg = json.loads(message)
        bar = msg['k']
        
        cur_datetime = datetime.fromtimestamp(bar['t']/1000, tz=tz)
        last_date = self.data.data["BTCUSDT"].iloc[-1].name.to_pydatetime()
        
        # print(cur_datetime, last_date)

        if abs(cur_datetime - last_date) < self.tolerance:
            # The datetime objects are equal within tolerance
            # print("The datetime objects are equal within tolerance")
            pass
        else:
            print("Update DataFrame")
            self.update_data(
                open_price=bar['o'],
                high_price=bar['h'],
                low_price=bar['l'],
                close_price=bar['c'],
                cur_datetime=cur_datetime
            )
            # print(self.data.data[self.symbol].get("Close").iloc[-1])
            # The datetime objects are not equal within tolerance
            # print("The datetime objects are not equal within tolerance")
            # pass
            adx, plusDI, minusDI = ADX(
                high=self.data.data[self.symbol].get("High"),
                low=self.data.data[self.symbol].get("Low"),
                close=self.data.data[self.symbol].get("Close"),
                period=14,
            )
            print("Time: ", cur_datetime)
            cur_plusDI = plusDI.iloc[-1]
            cur_muinusDI = minusDI.iloc[-1]
            
            if cur_plusDI > cur_muinusDI:
                print("PlusDI > MinusDI")
                
            else:
                print("PlusDI < MinusDI")
            print("PlusDI: ", cur_plusDI)
            print("MinusDI: ", cur_muinusDI)
            # print("ADX: ", adx.iloc[-1])
            # print("plusDI: ", plusDI.iloc[-1])
            # print("minusDI: ", minusDI.iloc[-1])
            # print("Open: ", bar['o'])
            # print("High: ", bar['h'])
            # print("Low: ", bar['l'])
            # print("Close: ", bar['c'])
        
            if self.orders:
                # print("Orders: ", self.orders)
                self.place_order(
                    open_price=bar['o'],
                    high_price=bar['h'],
                    low_price=bar['l'],
                    close_price=bar['c'],
                    date=cur_datetime
                )

            self.strategy(plusDI=plusDI.iloc[-1], minusDI=minusDI.iloc[-1], date=cur_datetime)
            
        
            print("-----"*10)
    
    def on_error(self, ws, error):
        print(error)
    
    def on_close(self, ws, close_status_code, close_msg):
        print("### closed ###")
        # print(self.data.data[self.symbol].info())
        # print(self.data.data[self.symbol])
        np.save("data_signal_no_drop.npy", np.array(self.list_of_orders))
    
    def on_open(self, ws):
        print("Opened connection")
        print("Preparing data...")
        date_now = datetime.now(tz=tz).replace(second=0, microsecond=0)
        start_date = date_now - timedelta(minutes=self.bar_range)
        # print(date_now, end_date)
        self.data = vbt.BinanceData.fetch(
            self.symbol,
            start=start_date,
            end=date_now,
            timeframe=self.timeframe,
            tz="Asia/Bangkok",
        )

    def update_data(
        self, 
        open_price : float, 
        high_price : float, 
        low_price : float, 
        close_price : float,
        cur_datetime : datetime
    ):
        add_list = [
            float(open_price), 
            float(high_price), 
            float(low_price), 
            float(close_price)
            , 0, 0, 0, 0, 0
        ]
        self.data.data[self.symbol].loc[cur_datetime] = add_list
        # self.data.data[self.symbol] = self.data.data[self.symbol].iloc[1:]
    
    def place_order(
        self,
        open_price : float, 
        high_price : float, 
        low_price : float, 
        close_price : float,
        date : datetime
    ):
        order_detail = self.orders.pop(0)
        order_detail["Place_date"] = date
        order_detail["Price"] = close_price
        
        self.list_of_orders.append(order_detail)
        
        if order_detail["Type"] == "Entry Long":
            print("Buy")
        elif order_detail["Type"] == "Exit Long":
            print("Sell")
        
    def strategy(self, plusDI: float, minusDI: float, date: datetime):
        buy_condition = plusDI > minusDI and plusDI > self.adx_level
        close_buy_condition = plusDI < minusDI
        close_buy_condition_2 = plusDI < self.adx_level
        
        if buy_condition and not self.orders and self.position == 0:
            # print("Buy")
            print("Signal Buy")
            self.position = 1
            self.orders.append({
                "Signal_date": date,
                "Type": "Entry Long",
                "Signal": "Buy",
                "plusDI": plusDI,
                "minusDI": minusDI,
            })
        if close_buy_condition and not self.orders and self.position > 0:
            # print("Sell")
            print("Signal Sell : plusDI < minusDI")
            self.position = 0
            self.orders.append({
                "Signal_date": date,
                "Type": "Exit Long",
                "Signal": "plusDI < minusDI",
                "plusDI": plusDI,
                "minusDI": minusDI,
            })
        if close_buy_condition_2 and not self.orders and self.position > 0:
            # print("Sell")
            print("Signal Sell : plusDI < adx_level")
            self.position = 0
            self.orders.append({
                "Signal_date": date,
                "Type": "Exit Long",
                "Signal": "plusDI < adx_level",
                "plusDI": plusDI,
                "minusDI": minusDI,
            })
            
    
adx = ADX_strategy()

ws = websocket.WebSocketApp(
    socket,
    on_open=adx.on_open,
    on_message=adx.on_message,
    on_error=adx.on_error,
    on_close=adx.on_close
)

ws.run_forever()

# api_key = os.environ['BINANCE_API_KEY_TEST']
# api_secret = os.environ['BINANCE_API_SECRET_TEST']

# url = 'https://api1.binance.com'

# client = Client(api_key, api_secret)

# res = client.get_server_time()
# print(res)
# str_time = "2023-04-11 16:13:00"
# xx = datetime.strptime(str_time, "%Y-%m-%d %H:%M:%S")
# print(xx)
# print(xx - timedelta(hours=3))
# your_dt = datetime.fromtimestamp(int(res['serverTime'])/1000)
# print(your_dt.strftime("%Y-%m-%d %H:%M:%S"))



# data = vbt.BinanceData.fetch(
#     "BTCUSDT",
#     start="2023-04-01",
#     # end="2021-01-01",
#     # limit=10,
#     timeframe="1 day"
# )
# print(data.data["BTCUSDT"])