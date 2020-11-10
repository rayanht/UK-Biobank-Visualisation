import dash_html_components as html
from dash.dependencies import ClientsideFunction, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd

from src.dash_app import app
from src.dataset_gateway import DatasetGateway, Query
from src.tree.node import NodeIdentifier

layout = dbc.Card(
    [
        html.H4("Summary statistics", className="summary-stats-title"),
        dbc.Table(id="statistics", size="sm"),
    ],
    style={"height": "15rem"},
    body=True,
)
