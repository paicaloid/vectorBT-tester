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

class Strategy:
    
    def __init__(self, period: int = 14, adx_level: int = 25) -> None:
        self.adx = None
        self.plusDI = None
        self.minusDI = None
        self.period = period
        self.adx_level = adx_level
        
        self.position = 0
        self.orders = []
        
        self.long_condition = False
        self.short_condition = False
        self.close_long_condition = False
        self.close_short_condition = False
        
    def create_order(self):
        
        if self.long_condition:
            if self.position < 0:
                self.orders.append("Exit Short")
            elif self.position > 0:
                pass
            elif self.position == 0:
                self.orders.append("Entry Long")
        
        if self.short_condition:
            if self.position > 0:
                self.orders.append("Exit Long")
            elif self.position < 0:
                pass
            elif self.position == 0:
                self.orders.append("Entry Short")
        
        if self.close_long_condition and self.position > 0:
            self.orders.append("Exit Long")
        
        if self.close_short_condition and self.position < 0:
            self.orders.append("Exit Short")
    

        
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
        
        # print("plusDI: ", self.plusDI)
        # print("minusDI: ", self.minusDI)
        # print("ADX: ", self.adx)
        # print("------------------")
        
        self.long_condition = (self.plusDI > self.minusDI) & (self.plusDI >= self.adx_level) 
        self.close_long_condition = (self.plusDI < self.minusDI) & (self.plusDI < self.adx_level)
        
        self.short_condition = (self.minusDI > self.plusDI) & (self.minusDI >= self.adx_level)
        self.close_short_condition = (self.minusDI < self.plusDI) & (self.minusDI < self.adx_level)
        
        open_order = False
        
        if self.long_condition:
            # * if current position is short, close it first before opening a long position
            if self.position < 0:
                self.orders.append("Exit Short")
                self.position = 0
                self.orders.append("Entry Long")
                self.position = 1
            # * if current position is long, work in progress with Take Profit and Stop Loss
            elif self.position > 0:
                pass
                # print("Setup TP/SL Long")
            # * if current position is none, open a long position
            elif self.position == 0:
                self.orders.append("Entry Long")
                self.position = 1
                
        
            
        if self.short_condition:
            # * if current position is long, close it first before opening a short position
            if self.position > 0:
                # print("Exit Long")
                self.orders.append("Exit Long")
                self.position = 0
                # print("Entry Short")
                self.orders.append("Entry Short")
                self.position = -1
                # open_order = True
                
            # * if current position is short, work in progress with Take Profit and Stop Loss
            elif self.position < 0:
                pass
                # print("Setup TP/SL Short")
            # * if current position is none, open a short position
            elif self.position == 0:
                # print("Entry Short")
                self.orders.append("Entry Short")
                self.position = -1
                # open_order = True
        
        if self.close_short_condition and self.position < 0:
            # print("Exit Short")
            self.orders.append("Exit Short")
            self.position = 0
            if self.long_condition:
                # print("Entry Long")
                self.orders.append("Entry Long")
                self.position = 1
            
        if self.close_long_condition and self.position > 0:
            # print("Exit Long")
            self.orders.append("Exit Long")
            self.position = 0
            if self.short_condition:
                # print("Entry Short")
                self.orders.append("Entry Short")
                self.position = -1
        
        # return open_order
        
class Backtest():
    
    def __init__(
        self, 
        symbol: str,
        lastest_date: datetime, 
        bar_range: int = 500,
        window_size: int = 250,
        cash: float = 1000.0
    ) -> None:
        
        self.symbol = symbol
        self.lastest_date = lastest_date
        self.bar_range = bar_range
        self.window_size = window_size
        self.cash = cash
        self.position = 0
        self.orders = []
        self.list_of_orders = []
        
    
    def get_historical_data(self) -> pd.DataFrame:
        # Get historical data
        start_date = self.lastest_date - timedelta(minutes=self.bar_range + self.window_size)
        print(start_date, self.lastest_date)
        data = vbt.BinanceData.fetch(
            self.symbol.upper(),
            start=start_date,
            end=self.lastest_date,
            timeframe="1 minutes",
            tz="Asia/Bangkok",
        )
        self.data = data.data[self.symbol.upper()]
        
    def simulate(self):
        
        self.strategy = Strategy()
        
        for index in range(self.bar_range + 1):
            
            data = self.data[index:index + self.window_size]
            
            # * Check if there is an open order
            # print(self.orders)
            if self.strategy.orders:
                print(data.index[-1], self.strategy.orders)
                self.strategy.orders = []
                self.orders = []
            # while self.orders:
            #     order = self.orders.pop(0)
            #     print(order)

            # print(data.index[-1])
            self.strategy.compute_signals(
                close_price=data["Close"],
                high_price=data["High"],
                low_price=data["Low"],
            )
            
            
            
if __name__ == '__main__':
    date = datetime.strptime("2023-04-18 16:00:00", "%Y-%m-%d %H:%M:%S")
    sim = Backtest(
        symbol="btcusdt", 
        lastest_date=date,
        bar_range=100
    )
    sim.get_historical_data()
    sim.simulate()
    print()