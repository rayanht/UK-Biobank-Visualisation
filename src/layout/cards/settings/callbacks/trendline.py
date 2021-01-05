import dash_core_components as dcc
from dash.dependencies import Input, Output
from src.dash_app import app


def get_trendline_dropdown(arg=None):
    return dcc.Dropdown(
        id="trendline-dropdown",
        options=[
            {"label": "Linear trendline", "value": 1},
            {"label": "Non-linear trendline", "value": 2},
            {"label": "No trendline", "value": 3},
        ],
        placeholder="Select a trendline",
        clearable=False,
        disabled=True,
    )


@app.callback(
    Output(component_id="trendline-dropdown", component_property="disabled"),
    Input(component_id="settings-graph-type-dropdown", component_property="value"),
)
def update_trendline_dropdown(value):
    return value != 2
