import json

from ws import ThreadClient

class TradingOrder:
    
    def __init__(self) -> None:
        pass
    

class Strategy:
    
    def __init__(self) -> None:
        pass
    

class StreamingCandlesticks(ThreadClient):
    
    def __init__(self, url, exchange) -> None:
        super().__init__(url, exchange)
        pass
    
class StreamingTickers:
    
    def __init__(self) -> None:
        pass
    
    def on_message(self, ws, message):
        msg = json.loads(message)
        print(msg)
        
symbol = 'btcusdt'
socket = f'wss://stream.binance.com:9443/ws/{symbol}@kline_1m'

# ws_binance = StreamingCandlesticks(
#     url=socket,
#     exchange='Binance'
# )

# ws_binance.start()

import asyncio
import websockets
import pytz
import pandas as pd
from datetime import datetime, timedelta
import vectorbtpro as vbt
import sqlalchemy

engine = sqlalchemy.create_engine('sqlite:///btcusdtStream.db')

class BinanceWebsocketHandler:
    def __init__(
        self, 
        symbol: str = "btcusdt", 
        interval: str = "1m", 
        trade: bool = True,
        bar_range: int = 250
    ) -> None:
        
        self.symbol = symbol
        self.tz = pytz.timezone('Asia/Bangkok')
        self.bar_range = bar_range
        
        self.connections = []
        self.connections.append(f'wss://stream.binance.com:9443/ws/{self.symbol}@kline_{interval}')
        if trade:
            self.connections.append(f'wss://stream.binance.com:9443/ws/{self.symbol}@trade')
        
        self.get_historical_data()
        
        self._first = True
        
            
    
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
        # print(self.data.iloc[:-1])
        print(self.data)
        # self.data.to_sql('btcusdt', engine, if_exists='append')
    
    def msg_to_dataframe(self, info: dict) -> pd.DataFrame:
        # close_time = info['T']
        # open_price = info['o']
        # close_price = info['c']
        # high_price = info['h']
        # low_price = info['l']
        # volume = info['v']
        # quote_volume = info['q']
        # trade_count = info['n']
        # taker_base_volume = info['V']
        # taker_base_quote_volume = info['Q']
        cur_datetime = datetime.fromtimestamp(info['t']/1000, tz=self.tz)
        # cur_datetime = cur_datetime.strftime('%Y-%m-%d %H:%M:%S%z')

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
        # df['Datetime'] = pd.to_datetime(df['Datetime'], unit='s', utc=True).dt.tz_convert('Asia/Bangkok')
        # df['Datetime'] = pd.to_datetime(df['Datetime'].apply(datetime.fromtimestamp))
        # df['Datetime'] = df['Datetime'].dt.tz_localize('UTC').dt.tz_convert('Asia/Bangkok')
        df['Datetime'] = cur_datetime
        df = df.set_index('Datetime')
        # df.to_sql('btcusdt', engine, if_exists='append')
        # print(df)
            
    
    async def handle_kline_message(self, message):
        msg = json.loads(message)
        bar = msg['k']
        
        is_close = bar['x']
        
        if is_close:
            print('Update...')
            self.msg_to_dataframe(info=bar)
        # else:
        #     s_time = datetime.fromtimestamp(bar['t']/1000, tz=self.tz)
        #     c_time = datetime.fromtimestamp(bar['T']/1000, tz=self.tz)
        #     print(f'Kline message received: {s_time} - {c_time}')
        # if self._first:
            # df = pd.DataFrame([bar])
            # print(df)
            # self.msg_to_dataframe(info=bar)
            # self._first = False
        # else:
        # cur_datetime = datetime.fromtimestamp(bar['t']/1000, tz=self.tz)
            # is_closed = bar['x']  
            # print(is_closed)
        # print(f'Kline message received: {cur_datetime} - {is_closed}')

    async def handle_trade_message(self, message):
        print(f'Trade message received')

    async def handle_socket(self, uri):
        async with websockets.connect(uri) as websocket:
            if 'kline' in uri:
                handle_message = self.handle_kline_message
            elif 'trade' in uri:
                handle_message = self.handle_trade_message
            async for message in websocket:
                await handle_message(message)

    async def run(self):
        await asyncio.wait([self.handle_socket(uri) for uri in self.connections])

if __name__ == '__main__':
    handler = BinanceWebsocketHandler(
        symbol='btcusdt',
        interval='1m',
        trade=False,
        bar_range=5
    )
    asyncio.get_event_loop().run_until_complete(handler.run())