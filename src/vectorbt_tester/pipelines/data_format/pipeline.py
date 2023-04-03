"""
This is a boilerplate pipeline 'data_format'
generated using Kedro 0.18.7
"""

from kedro.pipeline import Pipeline, node, pipeline

from .nodes import set_dataframe_index # custom node functions

def create_pipeline(**kwargs) -> Pipeline:
    return pipeline([
        node(
                func=set_dataframe_index,
                inputs=['RAW_GOOG_ADX', 'params:index_name'],
                outputs="GOOG_ADX",
                name="ADX_dataframe_index_node",
            ),
        node(
                func=set_dataframe_index,
                inputs=['RAW_GOOG_BB', 'params:index_name'],
                outputs="GOOG_BB",
                name="BB_dataframe_index_node",
            ),
        node(
                func=set_dataframe_index,
                inputs=['RAW_GOOG_EMA_5', 'params:index_name'],
                outputs="GOOG_EMA_5",
                name="EMA_5_dataframe_index_node",
            ),
        node(
                func=set_dataframe_index,
                inputs=['RAW_GOOG_EMA_35', 'params:index_name'],
                outputs="GOOG_EMA_35",
                name="EMA_35_dataframe_index_node",
            ),
        node(
                func=set_dataframe_index,
                inputs=['RAW_GOOG_MACD', 'params:index_name'],
                outputs="GOOG_MACD",
                name="MACD_dataframe_index_node",
            ),
        node(
                func=set_dataframe_index,
                inputs=['RAW_GOOG_OBV', 'params:index_name'],
                outputs="GOOG_OBV",
                name="OBV_dataframe_index_node",
            ),
        node(
                func=set_dataframe_index,
                inputs=['RAW_GOOG_RSI', 'params:index_name'],
                outputs="GOOG_RSI",
                name="RSI_dataframe_index_node",
            ),
        node(
                func=set_dataframe_index,
                inputs=['RAW_GOOG_SAR', 'params:index_name'],
                outputs="GOOG_SAR",
                name="SAR_dataframe_index_node",
            ),
        node(
                func=set_dataframe_index,
                inputs=['RAW_GOOG_STOCH', 'params:index_name'],
                outputs="GOOG_STOCH",
                name="STOCH_dataframe_index_node",
            ),
        node(
                func=set_dataframe_index,
                inputs=['RAW_GOOG_WR', 'params:index_name'],
                outputs="GOOG_WR",
                name="WR_dataframe_index_node",
            ),
    ])
