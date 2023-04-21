import json

from ws import ThreadClient
from adx import ADX

import asyncio
import websockets
import pytz
import pandas as pd
from datetime import datetime, timedelta
import vectorbtpro as vbt
import sqlalchemy

from typing import Union

class Strategy:
    
    def __init__(self, period: int = 14, adx_level: int = 25) -> None:
        self.adx = None
        self.plusDI = None
        self.minusDI = None
        self.period = period
        self.adx_level = adx_level
        
        self.position = 0
        self.orders = []
        self.df_trade = pd.DataFrame(columns=["Date", "Type", "Signal", "Price", "Size", "Profit"])
        
        self.long_condition = False
        self.short_condition = False
        self.close_long_condition = False
        self.close_short_condition = False
        
        self.tp_percent = 0.3
        self.sl_percent = 0.1
        
        self.long_tp = 0
        self.long_sl = 0
        self.short_tp = 0
        self.short_sl = 0
        
    def create_order(self):
        
        if self.long_condition:
            if self.position < 0:
                self.orders.append({"Type": "Exit Short", "Signal": "Buy"})
            elif self.position > 0:
                pass
            elif self.position == 0:
                self.orders.append({"Type": "Entry Long", "Signal": "Buy"})
        
        if self.short_condition:
            if self.position > 0:
                self.orders.append({"Type": "Exit Long", "Signal": "Sell"})
            elif self.position < 0:
                pass
            elif self.position == 0:
                self.orders.append({"Type": "Entry Short", "Signal": "Sell"})
        
        if self.close_long_condition and self.position > 0:
            self.orders.append("Exit Long")
        
        if self.close_short_condition and self.position < 0:
            self.orders.append("Exit Short")
    
    def print_order(self):
        order_print = False
        if self.long_condition:
            if self.position < 0:
                # print("Exit Short")
                self.position = 0
                order_print = True
                self.orders.append({"Type": "Exit Short", "Signal": "Close Short >> Buy"})
            elif self.position > 0:
                pass 
            elif self.position == 0:
                # print("Entry Long")
                self.position = 1
                order_print = True
                self.orders.append({"Type": "Entry Long", "Signal": "Buy"})
                
        if self.short_condition:
            if self.position > 0:
                # print("Exit Long")
                self.position = 0
                order_print = True
                self.orders.append({"Type": "Exit Long", "Signal": "Close Long >> Sell"})
            elif self.position < 0:
                pass
            elif self.position == 0:
                # print("Entry Short")
                self.position = -1
                order_print = True
                self.orders.append({"Type": "Entry Short", "Signal": "Sell"})
                
        if self.close_long_condition and self.position > 0:
            # print("Exit Long")
            self.position = 0
            order_print = True
            self.orders.append({"Type": "Exit Long", "Signal": "Close Long"})
            
        if self.close_short_condition and self.position < 0:
            # print("Exit Short")
            self.position = 0
            order_print = True
            self.orders.append({"Type": "Exit Short", "Signal": "Close Short"})
            
        
        
        return order_print
    
    def print_tp_sl(self, high_price: float, low_price: float):
        if self.position > 0 and self.long_tp != 0 and self.long_sl != 0:
            if low_price <= self.long_tp and self.long_tp <= high_price:
                # print("Take Profit")
                self.position = 0
                self.orders.append({"Type": "Exit Long", "Signal": "Take Profit"})
            elif low_price <= self.long_sl and self.long_sl <= high_price:
                # print("Stop Loss")
                self.position = 0
                self.orders.append({"Type": "Exit Long", "Signal": "Stop Loss"})
            
            
        elif self.position == -1:
            if self.short_tp >= low_price and self.short_tp <= high_price:
                # print("Take Profit")
                self.position = 0
                self.orders.append({"Type": "Exit Short", "Signal": "Take Profit"})
            elif self.short_sl >= low_price and self.short_sl <= high_price:
                # print("Stop Loss")
                self.position = 0
                self.orders.append({"Type": "Exit Short", "Signal": "Stop Loss"})
    
    def compute_signals(
        self,
        close_price: pd.Series,
        high_price: pd.Series,
        low_price: pd.Series,
    ) -> None:
        
        adx, plusDI, minusDI = ADX(
            high=high_price,
            low=low_price,
            close=close_price,
            period=self.period,
        )
        self.adx = adx.iloc[-1]
        self.plusDI = plusDI.iloc[-1]
        self.minusDI = minusDI.iloc[-1]

        self.long_condition = (self.plusDI > self.minusDI) & (self.plusDI >= self.adx_level) 
        self.close_long_condition = (self.plusDI < self.minusDI) & (self.plusDI < self.adx_level)
        
        self.short_condition = (self.minusDI > self.plusDI) & (self.minusDI >= self.adx_level)
        self.close_short_condition = (self.minusDI < self.plusDI) & (self.minusDI < self.adx_level)
    
    def execute_order(
        self,
        open_price: float,
        close_price: float,
        high_price: float,
        low_price: float,
        cur_date: datetime,
    ):
        order_info = self.orders.pop(0)
        
        if order_info["Type"] == "Entry Long":
            self.position = 1
            trade = {
                "Date": cur_date,
                "Type": order_info["Type"],
                "Signal": order_info["Signal"],
                "Price": open_price,
                "Size": 1,
                "Profit": 0,
            }
        elif order_info["Type"] == "Exit Long":
            self.position = 0
            trade = {
                "Date": cur_date,
                "Type": order_info["Type"],
                "Signal": order_info["Signal"],
                "Price": open_price,
                "Size": 1,
                "Profit": 0,
            }
        elif order_info["Type"] == "Entry Short":
            self.position = -1
            trade = {
                "Date": cur_date,
                "Type": order_info["Type"],
                "Signal": order_info["Signal"],
                "Price": open_price,
                "Size": 1,
                "Profit": 0,
            }
        elif order_info["Type"] == "Exit Short":
            self.position = 0
            trade = {
                "Date": cur_date,
                "Type": order_info["Type"],
                "Signal": order_info["Signal"],
                "Price": open_price,
                "Size": 1,
                "Profit": 0,
            }
        new_row = pd.DataFrame(trade, index=[0])
        # self.df_trade = self.df_trade.append(trade, ignore_index=True)
        self.df_trade = pd.concat([self.df_trade, new_row]).reset_index(drop=True)
        self.create_order()
    
class Backtest():
    
    def __init__(
        self, 
        symbol: str,
        lastest_date: datetime, 
        start_date: Union[datetime, None] = None ,
        bar_range: Union[int, None] = 100,
        window_size: int = 250,
        time_frame: str = "1m",
        cash: float = 1000.0
    ) -> None:
        
        self.symbol = symbol
        self.window_size = window_size
        self.lastest_date = lastest_date
        self.bar_range = bar_range
        
        if isinstance(start_date, datetime):
            self.start_date = start_date - timedelta(minutes=self.window_size)
            if time_frame == '1m':
                self.bar_range = int((end_date - start_date).total_seconds() / 60.0)
        else:
            if time_frame == '1m':
                self.start_date = self.lastest_date - timedelta(minutes=self.bar_range + self.window_size)
        

        
        self.cash = cash
        self.position = 0
        self.orders = []
        self.list_of_orders = []
        
    def simulate(self):
        
        self.strategy = Strategy()
        
        for index in range(1, self.bar_range + 1):
            
            data = self.data[index:index + self.window_size]
            
            # * Check if there is an open order
            while self.strategy.orders:
                order_info = self.strategy.orders.pop(0)                
                print(data.index[-1], "{0} \t {1}".format(order_info["Type"], order_info["Signal"]))
                if order_info["Type"] == "Entry Long":
                    self.strategy.long_tp = data["Open"].iloc[-1] * (1 + (self.strategy.tp_percent / 100))
                    self.strategy.long_sl = data["Open"].iloc[-1] * (1 - (self.strategy.sl_percent / 100))
                if order_info["Type"] == "Entry Short":
                    self.strategy.short_tp = data["Open"].iloc[-1] * (1 - (self.strategy.tp_percent / 100))
                    self.strategy.short_sl = data["Open"].iloc[-1] * (1 + (self.strategy.sl_percent / 100))
                
                # Re-create order after execute
                status = self.strategy.print_order()
                
            self.strategy.print_tp_sl(high_price=data["High"].iloc[-1], low_price=data["Low"].iloc[-1])
            while self.strategy.orders:
                order_info = self.strategy.orders.pop(0)                
                print(data.index[-1], "{0} \t {1}".format(order_info["Type"], order_info["Signal"]))
                self.strategy.long_tp = 0
                self.strategy.long_sl = 0
                self.strategy.short_tp = 0
                self.strategy.short_sl = 0

            # * Compute signals
            self.strategy.compute_signals(
                close_price=data["Close"],
                high_price=data["High"],
                low_price=data["Low"],
            )
            
            # * Create order
            status = self.strategy.print_order()

    def get_historical_data(self) -> pd.DataFrame:
        # Get historical data
        # start_date = self.lastest_date - timedelta(minutes=self.bar_range + self.window_size)
        # print(start_date, self.lastest_date)
        # start_date = self.start_date - timedelta(minutes=self.window_size)
    
        data = vbt.BinanceData.fetch(
            self.symbol.upper(),
            start=self.start_date,
            end=self.lastest_date,
            timeframe="1 minutes",
            tz="Asia/Bangkok",
        )                      
        self.data = data.data[self.symbol.upper()]
            
if __name__ == '__main__':
    start_date = datetime.strptime("2023-04-18 13:00:00", "%Y-%m-%d %H:%M:%S")
    end_date = datetime.strptime("2023-04-18 16:00:00", "%Y-%m-%d %H:%M:%S")
    sim = Backtest(
        symbol="btcusdt", 
        start_date=start_date,
        lastest_date=end_date,
        bar_range=239,
        window_size=250
    )
    sim.get_historical_data()
    # print(sim.data)
    sim.simulate()
    # print(sim.strategy.orders)
    # print(sim.strategy.df_trade)
    # print()