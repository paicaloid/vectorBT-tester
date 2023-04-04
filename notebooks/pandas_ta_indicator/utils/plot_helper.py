import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def plot_1_line(x: pd.Series(),y : pd.Series() ,title):
    fig = make_subplots(rows=1, cols=1)
    fig.append_trace(
        go.Scatter(
            x=x,
            y=y,
            line=dict(color='red', width=1),
            legendgroup='1',
        ), row=1, col=1
    )

    layout = go.Layout(
        plot_bgcolor='#efefef',
        width=1200,
        height = 400,
        font_family='Monospace',
        font_color='#000000',
        font_size=20,
        title=title,
        xaxis=dict(
            rangeslider=dict(
                visible=False
            )
        )
    )
    fig.update_layout(layout)
    fig.show()


def plot_2_line(x: pd.Series(),y1 : pd.Series() , y2 :pd.Series(), name_y1 , name_y2, title):
    fig = make_subplots(rows=1, cols=1)
    fig.append_trace(
        go.Scatter(
            x=x,
            y=y1,
            line=dict(color='red', width=1),
            name=name_y1,
            legendgroup='1',
        ), row=1, col=1
    )
    fig.append_trace(
        go.Scatter(
            x=x,
            y=y2,
            line=dict(color='blue', width=1),
            name=name_y2,
            legendgroup='1',
        ), row=1, col=1
    )

    layout = go.Layout(
        plot_bgcolor='#efefef',
        width=1200,
        height = 400,
        font_family='Monospace',
        font_color='#000000',
        font_size=20,
        title = title,
        xaxis=dict(
            rangeslider=dict(
                visible=False
            )
        )
    )
    fig.update_layout(layout)
    fig.show()



def plot_3_line(x: pd.Series(),y1 : pd.Series() , y2 :pd.Series(), y3: pd.Series(), name_y1 , name_y2, name_y3, title):
    fig = make_subplots(rows=1, cols=1)
    fig.append_trace(
        go.Scatter(
            x=x,
            y=y1,
            line=dict(color='red', width=1),
            name=name_y1,
            legendgroup='1',
        ), row=1, col=1
    )
    fig.append_trace(
        go.Scatter(
            x=x,
            y=y2,
            line=dict(color='blue', width=1),
            name=name_y2,
            legendgroup='1',
        ), row=1, col=1
    )

    fig.append_trace(
        go.Scatter(
            x=x,
            y=y3,
            line=dict(color='green', width=1),
            name=name_y3,
            legendgroup='1',
        ), row=1, col=1
    )
    layout = go.Layout(
        plot_bgcolor='#efefef',
        width=1200,
        height = 400,
        font_family='Monospace',
        font_color='#000000',
        font_size=20,
        title = title,
        xaxis=dict(
            rangeslider=dict(
                visible=False
            )
        )
    )
    fig.update_layout(layout)
    fig.show()