"""
This is a boilerplate pipeline 'rsi_strategy'
generated using Kedro 0.18.4
"""
from kedro.pipeline import Pipeline, node, pipeline
from kedro.io import DataCatalog
from kedro.extras.datasets.pandas.parquet_dataset import ParquetDataSet

import pandas as pd
import re
import vectorbt as vbt

from .nodes import select_asset, prepare_series, vbt_show, compute_rsi, strategy # custom node functions

def create_pipeline(**kwargs) -> Pipeline:
    return pipeline([
        node(
                func=select_asset,
                inputs=['GOOG_MERGE_DATA','params:asset'],
                outputs="ASSET_DATA",
                name="select_asset_node",
            ),
        node(
                func=prepare_series,
                inputs=['ASSET_DATA', 'params:price_type'],
                outputs="SERIES",
                name="data_series_node",
            ),
        node(
                func=compute_rsi,
                inputs=['SERIES', 'params:length'],
                outputs=['RSI', 'RSI_PLOT'],
                name="rsi_node",
            ),
        node(
                func=strategy,
                inputs=['RSI', 'ASSET_DATA', 'params:over_bought', 'params:over_sold'],
                outputs=['PORTFOLIO_RSI', 'PORTFOLIO_RSI_PLOT'],
                name='strategy_rsi_node'
            ),
    ])
