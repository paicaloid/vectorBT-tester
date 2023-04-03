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
                inputs=['RAW_GOOG', 'params:index_name'],
                outputs="GOOG",
                name="set_dataframe_index_node",
            ),
    ])
