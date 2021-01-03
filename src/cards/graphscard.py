import dash_html_components as html
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash_extensions import Download
from dash_extensions.snippets import send_data_frame
from src.dash_app import app
from dash.dependencies import Input, Output, State

import pandas as pd

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
                        dbc.Tooltip("Download plot as CSV", target="download-btn"),
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
        html.Div(children=[dcc.Graph(id="analysis-graph")], id="analysis-card")
    ],
}

tabs = [
    dbc.Tabs(
        [
            dbc.Tab(tab_id="metadata", label="Metadata plot"),
            dbc.Tab(tab_id="embedding", label="Embedding plot"),
        ],
        id="graphs-tabs",
        active_tab="metadata",
        card=True,
    )
]

layout = dbc.Card(
    [
        dbc.CardHeader(tabs),
        dbc.CardBody(
            dcc.Loading(
                [
                    html.Div(contents_by_id["metadata"], id="graphs-card-body"),

                    html.Div(id="loading-metadata-target", style={"display": "none"}),
                    html.Div(id="loading-umap-target", style={"display": "none"}),
                    html.Div(id="loading-tsne-target", style={"display": "none"})
                ],
                fullscreen=False,
                id="loading-wrapper"
            )
        )
    ],
    style={"height": "36rem"},  # for dummy purposes, to remove later
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
