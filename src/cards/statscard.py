import dash_html_components as html
from dash.dependencies import Input, Output, State
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


@app.callback(
    Output(component_id="statistics", component_property="children"),
    Input(component_id="json_filtered_data", component_property="children"),
    [
        State(component_id="variable-dropdown-x", component_property="value"),
        State(component_id="settings-graph-type-dropdown", component_property="value"),
    ],
)
def update_statistics(json_filtered_data, x_value, graph_type):
    """Update the summary statistics when the dropdown selection changes"""
    if ((x_value is None) | (json_filtered_data is None)):
        return str("Not much here")
    
    filtered_data = pd.read_json(json_filtered_data, orient='split')
    return dbc.Table.from_dataframe(
        filtered_data.describe().transpose(), striped=True, bordered=True, hover=True
    )
