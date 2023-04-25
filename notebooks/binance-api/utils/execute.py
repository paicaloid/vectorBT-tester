import pandas as pd

from datetime import datetime
from enum import Enum
from pydantic import BaseModel
from typing import List

from adx import ADX

class OrderType(Enum):
    entry_long = "Entry Long"
    entry_short = "Entry Short"
    exit_long = "Exit Long"
    exit_short = "Exit Short"

class Order(BaseModel):
    order_type: OrderType
    signal: str

class Portfoilo:
    
    def __init__(self, cash: float = 1000.0) -> None:
        self.cash = cash
        self.positions = 0
        self.port_value = 0
        self.list_of_trade = pd.DataFrame(columns=["Date", "Type", "Signal", "Price", "Size", "Profit"])
        

class ADX_Strategy(Portfoilo):
    
    def __init__(self, period: int = 14, adx_level: int = 25) -> None:
        
        super().__init__()
        
        self.adx = None
        self.plusDI = None
        self.minusDI = None
        self.period = period
        self.adx_level = adx_level
        
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
        
        self.orders: List[Order] = []
        
        
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
        
    def setup_condition(self) -> None:
        self.long_condition = (self.plusDI > self.minusDI) & (self.plusDI >= self.adx_level) 
        self.close_long_condition = (self.plusDI < self.minusDI) & (self.plusDI < self.adx_level)
        
        self.short_condition = (self.minusDI > self.plusDI) & (self.minusDI >= self.adx_level)
        self.close_short_condition = (self.minusDI < self.plusDI) & (self.minusDI < self.adx_level)
    
    def open_long(self) -> None:
        pass
    
    def place_order(
        self,
        open_price: float,
        high_price: float,
        low_price: float,
        close_price: float,
    ) -> None:
        
        if self.long_condition:
            if self.positions < 0:
                self.orders.append(Order(order_type=OrderType.exit_short, signal="Exit Short"))
            elif self.positions > 0:
                # self.set_long_tp_sl()
                pass
            else:
                self.orders.append(Order(order_type=OrderType.entry_long, signal="Entry Long"))
        
        if self.positions > 0:
            if self.close_long_condition:
                self.orders.append(Order(order_type=OrderType.exit_long, signal="Exit Long"))

        if self.short_condition:
            if self.positions > 0:
                self.orders.append(Order(order_type=OrderType.exit_long, signal="Exit Long"))
            elif self.positions < 0:
                # self.set_short_tp_sl()
                pass
            else:
                self.orders.append(Order(order_type=OrderType.entry_short, signal="Entry Short"))
        
        if self.positions < 0:
            if self.close_short_condition:
                self.close_short()
        
    def excute_order(
        self,
        cur_date: datetime,
        open_price: float,
        high_price: float,
        low_price: float,
        close_price: float,
    ) -> None:
        
        while self.orders:
            order = self.orders.pop(0)
            # print(f"{cur_date}     {order.signal:<10}")
            if order.order_type == OrderType.entry_long:
                self.positions = 1
                print(f"{cur_date}     {order.signal:<10}")
                self.port_value = open_price
            elif order.order_type == OrderType.entry_short:
                self.positions = -1
                print(f"{cur_date}     {order.signal:<10}")
                self.port_value = open_price
            elif order.order_type == OrderType.exit_long:
                self.positions = 0
                profit = (open_price - self.port_value)
                profit_percent = profit / self.port_value
                self.port_value = 0
                print(f"{cur_date}     {order.signal:<15} {profit:<10.2f} {profit_percent:<10.2%}")
                print("--------------------")
            elif order.order_type == OrderType.exit_short:
                self.positions = 0
                profit = (open_price - self.port_value) *  (-1)
                profit_percent = profit / self.port_value
                self.port_value = 0
                print(f"{cur_date}     {order.signal:<15} {profit:<10.2f} {profit_percent:<10.2%}")
                print("--------------------")
                
            
            # recalculate order
            self.place_order(
                open_price=open_price,
                high_price=high_price,
                low_price=low_price,
                close_price=close_price,
            )