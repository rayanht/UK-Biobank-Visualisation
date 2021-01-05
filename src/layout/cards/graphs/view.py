import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash_extensions import Download

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
                    html.Div(id="loading-tsne-target", style={"display": "none"}),
                ],
                fullscreen=False,
                id="loading-wrapper",
            )
        ),
    ],
    style={"height": "36rem"},  # for dummy purposes, to remove later
)
