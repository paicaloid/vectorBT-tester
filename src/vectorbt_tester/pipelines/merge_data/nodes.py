"""
This is a boilerplate pipeline 'merge_data'
generated using Kedro 0.18.7
"""
from kedro.pipeline import Pipeline, node, pipeline
from kedro.io import *
from kedro.runner import *

import pandas as pd
import json

from .nodes import * # your node functions

def set_dataframe_index(df: pd.DataFrame, index_name: str) -> pd.DataFrame:
	return df.set_index(index_name)

# def convert_to_json(df: pd.DataFrame):
#     df = df.reset_index()
#     json_string = df.to_json()
#     json_data = json.loads(json_string)
#     return json_data