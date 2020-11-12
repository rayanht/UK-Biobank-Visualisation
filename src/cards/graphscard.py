import dash_html_components as html
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash_extensions import Download
from dash_extensions.snippets import send_data_frame
from src.dash_app import app
from dash.dependencies import Input, Output, State

import pandas as pd

# Functions to get ids of components
from src.dataset_gateway import DatasetGateway, Query
from src.graph import get_statistics, prune_data, filter_data
from src.setting.instance_setting import get_dropdown_id as get_inst_dropdown_id
from src.setting.filter_setting import get_slider_id
from src.setting.plot_graph_setting import get_data_from_settings, get_filtered_data
from src.tree.node import NodeIdentifier

download_icon = html.I(id="submit-button", n_clicks=0, className="fa fa-download")

contents_by_id = {
    "metadata": [
        html.Div(
            [
                html.H4("Plot", className="mb-3 graphs-card-title"),
                html.Div(
                    [
                        dbc.Button(
                            children=download_icon,
                            id="download-btn",
                            color="primary",
                            outline=True,
                            n_clicks=0,
                            disabled=True,
                        ),
                        dbc.Tooltip(
                            "Download plot as CSV", target="download-btn"
                        ),
                    ],
                    className="ml-auto",
                ),
            ],
            className="d-flex",
        ),
        dcc.Graph(id="graph"),
        Download(id="download"),
    ],
    "embedding": [
        html.H3("Embedding plot"),
        dcc.Graph(id="graph-embedding")
    ]
}

tabs = [
    dbc.Tabs([
        dbc.Tab(tab_id="metadata", label="Metadata plot"),
        dbc.Tab(tab_id="embedding", label="Embedding plot")
    ], id="graphs-tabs", card=True)
]

layout = dbc.Card(
    [
        dbc.CardHeader(tabs),
        dbc.CardBody(
            contents_by_id["metadata"],
            id="graphs-card-body"
        )
    ],
    style={"height": "34rem"},  # for dummy purposes, to remove later
)


@app.callback(
    Output("download", "data"),
    [Input("download-btn", "n_clicks")],
    [State(component_id="plotted-data", component_property="data")],
)
def generate_csv(n_clicks, plotted_data):
    if n_clicks:
        data = pd.read_json(plotted_data, orient="split")
        return send_data_frame(
            data.to_csv, "ukbb_metadata_variable_subset.csv", index=False
        )

@app.callback(
    Output(component_id="statistics", component_property="children"),
    [
        Input(component_id="graph", component_property="selectedData"),
        Input(component_id="settings-card-submit", component_property="n_clicks"),
    ],
    [
        State(component_id="graph-data", component_property="data"),
        State(component_id=get_inst_dropdown_id("x"), component_property="value"),
        State(component_id=get_inst_dropdown_id("y"), component_property="value"),
        State(component_id="settings-graph-type-dropdown", component_property="value"),
        # colour
        State(
            component_id="settings-graph-colour-dropdown", component_property="value"
        ),
        # filters
        State(component_id=get_slider_id("x"), component_property="value"),
        State(component_id=get_slider_id("y"), component_property="value"),
    ],
)
def update_statistics(
    selected_data,
    n,
    cached_data,
    x_value,
    y_value,
    graph_type,
    colour,
    x_filter,
    y_filter,
):
    ctx = dash.callback_context
    df = None
    node_id_x = None
    node_id_y = None

    if not ctx.triggered:
        trigger = "No clicks yet"
    else:
        trigger = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger == "settings-card-submit":
        data, new_cached_data, node_id_x, node_id_y = get_data_from_settings(
            cached_data, x_value, y_value, colour, x_filter, y_filter
        )

        if data is None:
            return "No data to display"

        # filter data
        _, df = get_filtered_data(data, x_value, y_value, x_filter, y_filter)
    elif trigger == "graph":
        points = selected_data["points"]
        points = [(p["x"], p["y"]) for p in points]
        points_x, points_y = zip(*points)
        node_id_x = None
        node_id_y = NodeIdentifier(y_value)
        if x_value is not None:
            node_id_x = NodeIdentifier(x_value)
            df = pd.DataFrame({"x": points_x})
        if y_value is not None:
            node_id_y = NodeIdentifier(y_value)
            df = pd.DataFrame({"x": points_x, "y": points_y})

    return get_statistics(df, x_value, node_id_x, y_value, node_id_y)