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


class Portfolio:
    
    def __init__(self, cash: float = 1000.0) -> None:
        self.cash = cash
        self.position = 0
        self.orders = []
        self.list_of_orders = []
    

class Strategy:
    
    def __init__(self, period: int = 14, adx_level: int = 25) -> None:
        self.adx = None
        self.plusDI = None
        self.minusDI = None
        self.period = period
        self.adx_level = adx_level
        
        self.long_condition = False
        self.short_condition = False
        self.close_long_condition = False
        self.close_short_condition = False
        
        self.position = 0
        self.orders = []
    
    def compute_signals(
        self,
        open_price: pd.Series,
        high_price: pd.Series,
        low_price: pd.Series,
    ) -> None:
        adx, plusDI, minusDI = ADX(
            high=high_price,
            low=low_price,
            close=open_price,
            period=self.period,
        )
        
        self.adx = adx.iloc[-1]
        self.plusDI = plusDI.iloc[-1]
        self.minusDI = minusDI.iloc[-1]
        
        print("plusDI: ", self.plusDI)
        print("minusDI: ", self.minusDI)
        print("ADX: ", self.adx)
        print("------------------")
        
        self.long_condition = (self.plusDI > self.minusDI) & (self.plusDI >= self.adx_level) 
        self.close_long_condition = (self.plusDI < self.minusDI) & (self.plusDI < self.adx_level)
        
        self.short_condition = (self.minusDI > self.plusDI) & (self.minusDI >= self.adx_level)
        self.close_short_condition = (self.minusDI < self.plusDI) & (self.minusDI < self.adx_level)
        
        order_info = {}
        if self.long_condition and self.position == 0:
            print("Entry Long")
            self.position = 1
        if self.close_long_condition and self.position > 0:
            print("Exit Long")
            self.position = 0
        if self.short_condition and self.position == 0:
            print("Entry Short")
            self.position = -1
        if self.close_short_condition and self.position < 0:
            print("Exit Short")
            self.position = 0
        print("++++++++++++++++++++")

    def create_order_info(self, type: str, signal: str, cur_date: datetime) -> dict:
        # cur_date = datetime.now(tz=pytz.timezone("Asia/Bangkok")).replace(second=0, microsecond=0)
        order_info = {
            "Signal Date": cur_date,
            "plusDI": self.plusDI,
            "minusDI": self.minusDI,
            "ADX": self.adx,
            "Type": type,
            "Signal": signal,
        }
        return order_info
    
    def place_order(
        self,
        df: pd.DataFrame,
    ):
        # if self.orders:
        #     order_detail = self.orders.pop(0)
        #     order_detail["Place_date"] = date
        #     order_detail["Price"] = close_price
            
        #     self.list_of_orders.append(order_detail)
            
        #     if order_detail["Type"] == "Entry Long":
        #         print("Buy")
        #     elif order_detail["Type"] == "Exit Long":
        #         print("Sell")
        pass
    
    def calculate_order(self, cur_date: datetime):
        # cur_date = datetime.now(tz=pytz.timezone("Asia/Bangkok")).replace(second=0, microsecond=0)
        order_info = {}
        if self.long_condition and self.position == 0:
            order_info = self.create_order_info(type="Entry Long", signal="Buy", cur_date=cur_date)
        if self.close_long_condition and self.position > 0:
            order_info = self.create_order_info(type="Exit Long", signal="Sell", cur_date=cur_date)
        if self.short_condition and self.position == 0:
            order_info = self.create_order_info(type="Entry Short", signal="Sell", cur_date=cur_date)
        if self.close_short_condition and self.position < 0:
            order_info = self.create_order_info(type="Exit Short", signal="Buy", cur_date=cur_date)
            
        if order_info:
            print(order_info)
            self.orders.append(order_info)


engine = sqlalchemy.create_engine('sqlite:///btcusdtStream.db')

class BinanceWebsocketHandler:
    def __init__(
        self, 
        symbol: str = "btcusdt", 
        interval: str = "1m", 
        trade: bool = True,
        bar_range: int = 250,
        sql: bool = True
    ) -> None:
        
        self.symbol = symbol
        self.tz = pytz.timezone('Asia/Bangkok')
        self.bar_range = bar_range
        self.sql = sql
        
        self.connections = []
        self.connections.append(f'wss://stream.binance.com:9443/ws/{self.symbol}@kline_{interval}')
        if trade:
            # self.connections.append(f'wss://stream.binance.com:9443/ws/{self.symbol}@trade')
            self.connections.append(f'wss://stream.binance.com:9443/ws/{self.symbol}@kline_1s')
            
        self.get_historical_data()
        self.indicators = Strategy(adx_level=20)
        
    def get_historical_data(self) -> None:
        print("Preparing data...")
        date_now = datetime.now(tz=self.tz).replace(second=0, microsecond=0)
        start_date = date_now - timedelta(minutes=self.bar_range)
        
        data = vbt.BinanceData.fetch(
            self.symbol.upper(),
            start=start_date,
            end=date_now,
            timeframe="1 minutes",
            tz="Asia/Bangkok",
        )
        self.data = data.data[self.symbol.upper()]
        self.data.index = self.data.index.rename('Datetime')

        if self.sql:
            self.data.to_sql('btcusdt', engine, if_exists='append')
    
    def msg_to_dataframe(self, info: dict, interval: str) -> pd.DataFrame:
        
        cur_datetime = datetime.fromtimestamp(info['t']/1000, tz=self.tz)
        df = pd.DataFrame([info])
        df = df.drop(['T','t', 's', 'i', 'f', 'L', 'x', 'B'], axis=1)
        df = df.rename(columns={
            'o': 'Open',
            'h': 'High',
            'l': 'Low',
            'c': 'Close',
            'v': 'Volume',
            'q': 'Quote volume',
            'n': 'Trade count',
            'V': 'Taker base volume',
            'Q': 'Taker quote volume'
        })
        df = df.astype(float)
        df["Trade count"] = df["Trade count"].astype(int)

        df['Datetime'] = cur_datetime
        df = df.set_index('Datetime')
        
        if self.sql:
            df.to_sql(f'btcusdt_{interval}', engine, if_exists='append')
            
        return df
    
    def update_dataframe(self, lastest_df: pd.DataFrame) -> None:
        self.data = pd.concat([self.data, lastest_df])
        self.data = self.data[-self.bar_range:]
        # print(self.data)
    
    async def handle_kline_1m_message(self, message) -> None:
        msg = json.loads(message)
        # ref https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-streams.md#klinecandlestick-streams
        bar = msg['k']
        is_close = bar['x']
        
        if is_close:
            cur_date = datetime.fromtimestamp(bar['t']/1000, tz=self.tz)
            # Place orders if possible
            
            
            # Update dataframe
            # print('Update...')
            df = self.msg_to_dataframe(info=bar, interval="1m")
            self.update_dataframe(lastest_df=df)
            
            # Calculate indicators
            self.indicators.compute_signals(
                open_price=self.data['Open'],
                high_price=self.data['High'],
                low_price=self.data['Low'],
            )
            
            # Create order for next bar
            # self.indicators.calculate_order(cur_date=cur_date)

    async def handle_kline_1s_message(self, message):
        # print(f'Trade message received')
        msg = json.loads(message)
        bar = msg['k']
        is_close = bar['x']
        if is_close:
            df = self.msg_to_dataframe(info=bar, interval="1m")
        
    async def handle_socket(self, uri):
        async with websockets.connect(uri) as websocket:
            if 'kline_1m' in uri:
                handle_message = self.handle_kline_1m_message
            elif 'kline_1s' in uri:
                handle_message = self.handle_kline_1s_message
            async for message in websocket:
                await handle_message(message)

    async def run(self):
        await asyncio.wait([self.handle_socket(uri) for uri in self.connections])

if __name__ == '__main__':
    handler = BinanceWebsocketHandler(
        symbol='btcusdt',
        interval='1m',
        trade=False,
        bar_range=250,
        sql=False
    )
    asyncio.get_event_loop().run_until_complete(handler.run())