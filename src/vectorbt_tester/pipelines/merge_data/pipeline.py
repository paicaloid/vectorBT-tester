"""
This is a boilerplate pipeline 'merge_data'
generated using Kedro 0.18.7
"""
from kedro.pipeline import Pipeline, node, pipeline
from kedro.io import DataCatalog
from kedro.extras.datasets.pandas.parquet_dataset import ParquetDataSet

import pandas as pd
import re

from .nodes import set_dataframe_index # custom node functions

def partition_data(partitions: DataCatalog, index_name: str) -> ParquetDataSet:
    df = pd.DataFrame()
    r = re.compile("time*") # no suffix for column 'time'
    for data_name in partitions:
        # asset_name = re.split('_', data_name)[0] # ['GOOG', '1D', 'WR']
        asset_name = data_name
        data = partitions[data_name]()
        data = data[['time', 'open', 'high', 'low', 'close']]
        data = data.add_suffix(f'_{asset_name}')
        time_col = list(filter(r.match, data.columns))[0]
        data = data.rename(columns = {time_col: 'time'})
        if df.empty:
            df = data
        else:
            df = df.merge(data, how='outer', on='time')
    return set_dataframe_index(df, index_name)

def plot_df(df: pd.DataFrame):
    df = df.reset_index() # to set index column 'time' as a normal column 
    return df

def create_pipeline(**kwargs) -> Pipeline:
    pipeline = Pipeline(
        [
            node(
                partition_data,
                inputs=['RAW_GOOG_DATASET', 'params:index_name'],
                outputs='GOOG_MERGE_DATA',
                name='partition_data_node',
            ),
            node(
                func=plot_df,
                inputs='GOOG_MERGE_DATA',
                outputs='GOOG_PLOT',
                name='plot_node'
            ),
        ]
    )
    return pipeline
