import pandas as pd
import vectorbtpro as vbt

from datetime import datetime, timedelta
from typing import Union

from execute import ADX_Strategy

class Backtest:
    
    def __init__(
        self, 
        symbol: str,
        lastest_date: datetime, 
        start_date: Union[datetime, None] = None ,
        bar_range: Union[int, None] = 100,
        window_size: int = 250,
        time_frame: str = "1m",
    ) -> None:
        
        self.symbol = symbol
        self.window_size = window_size
        self.lastest_date = lastest_date
        self.bar_range = bar_range
        
        if isinstance(start_date, datetime):
            self.start_date = start_date - timedelta(minutes=self.window_size)
            if time_frame == '1m':
                self.bar_range = int((self.lastest_date - start_date).total_seconds() / 60.0)
        else:
            if time_frame == '1m':
                self.start_date = self.lastest_date - timedelta(minutes=self.bar_range + self.window_size)
    
    def get_historical_data(self) -> pd.DataFrame:
        data = vbt.BinanceData.fetch(
            self.symbol.upper(),
            start=self.start_date,
            end=self.lastest_date,
            timeframe="1 minutes",
            tz="Asia/Bangkok",
        )                      
        self.data = data.data[self.symbol.upper()]
        
    def simualte(self) -> None:
        self.strategy = ADX_Strategy(adx_level=19)
        
        for index in range(1, self.bar_range + 1):
            data = self.data[index:index + self.window_size]
            cur_date = data.index[-1]
            open_price = data["Open"].iloc[-1]
            high_price = data["High"].iloc[-1]
            low_price = data["Low"].iloc[-1]
            close_price = data["Close"].iloc[-1]
            
            # * 1. Execute order
            # * 1.1 If possible, recalculate and Execute order again
            self.strategy.excute_order(
                cur_date=cur_date,
                open_price=open_price,
                high_price=high_price,
                low_price=low_price,
                close_price=close_price,
            )
            
            # * 2. Compute signal
            self.strategy.compute_signals(
                close_price=data["Close"],
                high_price=data["High"],
                low_price=data["Low"],
            )
            
            # * 3. Setup condition
            self.strategy.setup_condition()
            
            # * 4. Place order
            self.strategy.place_order(
                open_price=open_price,
                high_price=high_price,
                low_price=low_price,
                close_price=close_price,
            )
        
if __name__ == '__main__':
    start_date = datetime.strptime("2023-04-18 13:00:00", "%Y-%m-%d %H:%M:%S")
    end_date = datetime.strptime("2023-04-18 14:00:00", "%Y-%m-%d %H:%M:%S")
    sim = Backtest(
        symbol="btcusdt", 
        start_date=start_date,
        lastest_date=end_date,
        bar_range=239,
        window_size=250
    )
    sim.get_historical_data()
    sim.simualte()