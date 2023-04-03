"""
This is a boilerplate pipeline 'data_format'
generated using Kedro 0.18.7
"""
#from kedro.pipeline import *
from kedro.pipeline import Pipeline, node, pipeline
from kedro.io import *
from kedro.runner import *

import pandas as pd

from .nodes import * # your node functions

def set_dataframe_index(df: pd.DataFrame, index_name: str):
	return df.set_index(index_name)