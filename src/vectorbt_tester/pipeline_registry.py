"""Project pipelines."""
from typing import Dict

from kedro.framework.project import find_pipelines
from kedro.pipeline import Pipeline

from vectorbt_tester.pipelines import data_format as df
from vectorbt_tester.pipelines import merge_data as md
from vectorbt_tester.pipelines import rsi_strategy as rsi_s
from vectorbt_tester.pipelines import ma_strategy as ma_s

def register_pipelines() -> Dict[str, Pipeline]:
    """Register the project's pipelines.

    Returns:
        A mapping from pipeline names to ``Pipeline`` objects.
    """
    # # 0. In DEFAULT case
    # pipelines = find_pipelines()
    # pipelines["__default__"] = sum(pipelines.values())

    # return pipelines
    
    # 1. In case that you want to rename pipeline
    data_format_pipeline = df.create_pipeline()
    rsi_stategy_pipeline = md.create_pipeline() + rsi_s.create_pipeline()
    ma_stategy_pipeline = md.create_pipeline() + ma_s.create_pipeline()

    return {
        "data format": data_format_pipeline,
        "rsi stategy": rsi_stategy_pipeline,
        "ma stategy": ma_stategy_pipeline, 
        "__default__": data_format_pipeline + rsi_stategy_pipeline + ma_stategy_pipeline,
    }
