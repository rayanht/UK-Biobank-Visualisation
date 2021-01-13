import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash_extensions import Download


download_icon = html.I(id="submit-button", n_clicks=0, className="fa fa-download")

contents = [
    html.Div(
        [
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
        ]
    ),
    html.Div(dcc.Graph(id="embedding-graph"), style={"display": "None"}),
    html.Div(dcc.Graph(id="clustering-graph"), style={"display": "None"}),
]

tabs = [
    dbc.Tabs(
        [
            dbc.Tab(tab_id="metadata", label="Data plot"),
            dbc.Tab(tab_id="embedding", label="Embedding"),
            dbc.Tab(tab_id="clustering", label="Clustering"),
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
                    html.Div(contents, id="graphs-card-body"),
                    html.Div(id="loading-metadata-target", style={"display": "none"}),
                    html.Div(
                        id="loading-dimensionality-target", style={"display": "none"}
                    ),
                ],
                fullscreen=False,
                id="loading-wrapper",
            )
        ),
    ],
    style={"height": "36rem"},  # for dummy purposes, to remove later
)
