"""Project pipelines."""
from typing import Dict

from kedro.framework.project import find_pipelines
from kedro.pipeline import Pipeline

from vectorbt_tester.pipelines import data_format as df
from vectorbt_tester.pipelines import merge_data as md


def register_pipelines() -> Dict[str, Pipeline]:
    """Register the project's pipelines.

    Returns:
        A mapping from pipeline names to ``Pipeline`` objects.
    """
    # 0. In DEFAULT case
    pipelines = find_pipelines()
    pipelines["__default__"] = sum(pipelines.values())

    return pipelines
    
    # # 1. In case that you want to rename pipeline
    # data_format_pipeline = df.create_pipeline()
    # merge_data_pipeline = md.create_pipeline()

    # return {
    #     "df": data_format_pipeline,
    #     "md": merge_data_pipeline,
    #     "__default__": data_format_pipeline + merge_data_pipeline,
    # }
