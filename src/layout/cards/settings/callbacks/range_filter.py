import time

import pandas as pd
import dash_core_components as dcc
import dash_html_components as html

from dataset_gateway import Query, DatasetGateway
from src.dash_app import dash, app

from dash.dependencies import Input, MATCH, Output, State
from src.tree.node import NodeIdentifier
from .instance_selection import get_dropdown_id as get_instance_dropdown_id


def get_option_dropdown(var: str):
    return html.Div(
        id={"var": var, "type": "filter-slider-div"},
        children=[
            html.H6("Filter values", className="mt-2"),
            dcc.RangeSlider(
                id={"var": var, "type": "filter-slider"},
                allowCross=False,
                tooltip={"always_visible": False, "placement": "bottom"},
            ),
        ],
        style={"display": "none"},
    )


def get_slider_id(var=MATCH):
    return {"var": var, "type": "filter-slider"}


def get_div_id(var=MATCH):
    return {"var": var, "type": "filter-slider-div"}


@app.callback(
    [
        Output(component_id=get_slider_id(), component_property="min"),
        Output(component_id=get_slider_id(), component_property="max"),
        Output(component_id=get_slider_id(), component_property="value"),
        Output(component_id=get_slider_id(), component_property="marks"),
        Output(component_id=get_div_id(), component_property="style"),
    ],
    [Input(component_id=get_instance_dropdown_id(), component_property="value")],
)
def update_settings_options(value):
    """
    Callback to update the visibility of the range filters.

    :param value: the data field that is currently selected in either axis
    :return: a HTML div of the range slider
    """
    if not value:
        return (dash.no_update, dash.no_update, None, dash.no_update, dash.no_update)

    # Normalise the identifier
    node_id = NodeIdentifier(value)

    # Query the database for min and max
    min_max = DatasetGateway.submit(Query.from_identifier(node_id).get_min_max())
    df_min = int(min_max["min"].values[0])
    df_max = int(min_max["max"].values[0] + 1)
    return (
        df_min,
        df_max,
        [df_min, df_max],
        {df_min: str(df_min), df_max: str(df_max)},
        {"display": "block"},
    )
