"""
This is a boilerplate pipeline 'ma_strategy'
generated using Kedro 0.18.4
"""
from kedro.pipeline import Pipeline, node, pipeline
from kedro.io import *
from kedro.runner import *

import pandas as pd
import json
import vectorbt as vbt

from .nodes import * # your node functions

def select_asset(df: pd.DataFrame, asset: str) -> pd.Series:
    col_map = {f"open_{asset}": 'open', f'close_{asset}': 'close', f'high_{asset}': 'hight', f'low_{asset}': 'low'}
    select_col = col_map.keys()
    asset_df = df[select_col]
    asset_df = asset_df.rename(columns=col_map)
    return asset_df

def prepare_series(df: pd.DataFrame,  price_type: str) -> pd.Series:
    # df = set_dataframe_index(df, index_name)
    df = df[price_type]
    return df

def vbt_show(data: vbt.indicators.basic.MA or vbt.portfolio.base.Portfolio) -> vbt.utils.figure.FigureWidget:
    return data.plot()

def compute_ma(data: pd.Series, slow: int, fast: int) -> [vbt.indicators.basic.MA, vbt.indicators.basic.MA, vbt.utils.figure.FigureWidget, vbt.utils.figure.FigureWidget]:
    slow_ma = vbt.MA.run(data, slow)
    fast_ma = vbt.MA.run(data, fast)
    # combine graph
    ma_plot = data.vbt.plot(trace_kwargs=dict(name='Price'))
    slow_ma.ma.vbt.plot(trace_kwargs=dict(name=f'Slow MA({slow})'), fig=ma_plot)
    fast_ma.ma.vbt.plot(trace_kwargs=dict(name=f'Fast MA({fast})'), fig=ma_plot)
    return slow_ma, fast_ma, ma_plot

def strategy(slow_ma: vbt.indicators.basic.MA, fast_ma: vbt.indicators.basic.MA, price_df: pd.DataFrame) -> [vbt.portfolio.base.Portfolio, vbt.utils.figure.FigureWidget]:
    open = price_df['open']
    close = price_df['close']
    hight = price_df['hight']
    low = price_df['low']
    entries = fast_ma.ma_above(slow_ma)
    exits = slow_ma.ma_above(fast_ma)
    pf = vbt.Portfolio.from_signals(close, entries, exits)
    return pf, vbt_show(pf)
