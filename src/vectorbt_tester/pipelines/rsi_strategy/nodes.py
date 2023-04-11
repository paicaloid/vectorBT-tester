"""
This is a boilerplate pipeline 'rsi_strategy'
generated using Kedro 0.18.4
"""
from kedro.pipeline import Pipeline, node, pipeline
from kedro.io import *
from kedro.runner import *

import pandas as pd
import json
import vectorbt as vbt

from .nodes import * # your node functions

# def set_dataframe_index(df: pd.DataFrame, index_name: str) -> pd.DataFrame:
# 	return df.set_index(index_name)

def select_asset(df: pd.DataFrame, asset: str) -> pd.Series:
    col_map = {f"open_{asset}": 'open', f'close_{asset}': 'close', f'high_{asset}': 'hight', f'low_{asset}': 'low'}
    select_col = col_map.keys()
    asset_df = df[select_col]
    asset_df = asset_df.rename(columns=col_map)
    return asset_df

def compute_rsi(data: pd.Series, length: int) -> pd.DataFrame:
    rsi = vbt.RSI.run(data, window=length)
    return rsi, vbt_show(rsi)

def prepare_series(df: pd.DataFrame,  price_type: str) -> pd.Series:
    # df = set_dataframe_index(df, index_name)
    df = df[price_type]
    return df

def vbt_show(data: vbt.indicators.basic.RSI or vbt.portfolio.base.Portfolio) -> vbt.utils.figure.FigureWidget:
    return data.plot()

def strategy(rsi: vbt.indicators.basic.RSI, price_df: pd.DataFrame, over_bought: int, over_sold: int):
    open = price_df['open']
    close = price_df['close']
    hight = price_df['hight']
    low = price_df['low']
    entries = rsi.rsi_crossed_above(over_bought)
    exits = rsi.rsi_crossed_below(over_sold)
    pf = vbt.Portfolio.from_signals(close, entries, exits)
    return pf, vbt_show(pf)