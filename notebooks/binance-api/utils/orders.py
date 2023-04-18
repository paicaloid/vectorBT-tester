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
            self.connections.append(f'wss://stream.binance.com:9443/ws/{self.symbol}@trade')
        
        self.get_historical_data()
        
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
    
    def msg_to_dataframe(self, info: dict) -> pd.DataFrame:
        
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
            df.to_sql('btcusdt', engine, if_exists='append')
            
        return df
    
    def update_dataframe(self, lastest_df: pd.DataFrame) -> None:
        self.data = pd.concat([self.data, lastest_df])
        self.data = self.data[-self.bar_range:]
        print(self.data)
    
    async def handle_kline_message(self, message) -> None:
        msg = json.loads(message)
        # ref https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-streams.md#klinecandlestick-streams
        bar = msg['k']
        is_close = bar['x']
        
        if is_close:
            print('Update...')
            df = self.msg_to_dataframe(info=bar)
            self.update_dataframe(lastest_df=df)


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
        bar_range=5,
        sql=False
    )
    asyncio.get_event_loop().run_until_complete(handler.run())