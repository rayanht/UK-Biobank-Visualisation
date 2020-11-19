import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
from src.dash_app import dash, app

from dash.dependencies import Input, MATCH, Output, State
from src.tree.node import NodeIdentifier
from src.setting.instance_setting import get_dropdown_id as get_instance_dropdown_id


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


# update options (possibly merge with apply_graph_settings to prevent sending cached_data twice?)
@app.callback(
    [
        Output(component_id=get_slider_id(), component_property="min"),
        Output(component_id=get_slider_id(), component_property="max"),
        Output(component_id=get_slider_id(), component_property="value"),
        Output(component_id=get_slider_id(), component_property="marks"),
        Output(component_id=get_div_id(), component_property="style"),
    ],
    [
        Input(component_id="graph-data", component_property="data"),
        Input(component_id=get_instance_dropdown_id(), component_property="value"),
    ],
    [State(component_id=get_instance_dropdown_id(), component_property="id")],
)
def update_settings_options(cached_data, value, id):
    var = id["var"]
    filter_tuple = (
        dash.no_update,
        dash.no_update,
        None,
        dash.no_update,
        dash.no_update,
    )

    if not cached_data:
        return filter_tuple

    # update settings
    if cached_data[f"{var}-value"] != "":
        filtered_data = pd.read_json(cached_data["data"], orient="split")
        filter_tuple = get_range_slider_tuple(
            filtered_data, value, cached_data[f"{var}-value"]
        )

    return filter_tuple


def get_range_slider_tuple(filtered_data, curr_value, stored_value):
    if not curr_value or stored_value != curr_value:
        return (
            dash.no_update,
            dash.no_update,
            None,
            dash.no_update,
            {"display": "none"},
        )
    node_id = NodeIdentifier(stored_value)
    df = filtered_data[node_id.db_id()]
    df_min = int(df.min())
    df_max = int(df.max())
    return (
        df_min,
        df_max,
        [df_min, df_max],
        {df_min: str(df_min), df_max: str(df_max)},
        {"display": "block"},
    )
