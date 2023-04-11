"""
This is a boilerplate pipeline 'ma_strategy'
generated using Kedro 0.18.4
"""

from kedro.pipeline import Pipeline, node, pipeline

from .nodes import select_asset, prepare_series, vbt_show, compute_ma, strategy # custom node functions

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
                func=compute_ma,
                inputs=['SERIES', 'params:slow_length', 'params:fast_length'],
                outputs=['SLOW_MA', 'FAST_MA', 'MA_PLOT'],
                name="ma_node",
            ),
        node(
                func=strategy,
                inputs=['SLOW_MA', 'FAST_MA', 'ASSET_DATA'],
                outputs=['PORTFOLIO_MA', 'PORTFOLIO_MA_PLOT'],
                name='strategy_ma_node'
            ),
    ])
