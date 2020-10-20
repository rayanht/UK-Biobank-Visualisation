import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import re

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from src.dataset_gateway import MetaDataLoader
from src.graph import ValueType

mt = MetaDataLoader()

def update_settings_card(n, selected) :
    if (len(selected) == 0): 
        return [
            dbc.CardBody(
                [
                    html.H4("Settings", className="settings-card-title"),
                    dbc.Label("Please select a data category", html_for="settings-empty"),
                ]
            )
        ]

    field_id = selected[0] # Only supports one variable for now

    df = mt.field_id_meta_data
    value_type_id = int(df.loc[df['field_id'] == str(field_id)]['value_type'].values[0])
    value_type = ValueType(value_type_id)
    
    options = [
        {"label": "Violin", "value": 1},
        {"label": "Scatter", "value": 2},
        {"label": "Bar", "value": 3},
        {"label": "Pie", "value": 4},
    ]

    supported_graphs = value_type.supported_graphs

    graph_selection_list = []
    disabled_graphs = []

    for x in range(len(options)):
        graph_type = options[x]["value"]
        if (graph_type in supported_graphs):
            graph_selection_list.append(options[x])
        else:
            options[x]["disabled"] = True
            disabled_graphs.append(options[x])

    graph_selection_list.extend(disabled_graphs)

    return [
        dbc.CardBody(
                [
                    html.H4("Settings", className="settings-card-title"),
                    dbc.Label("Graph Type", html_for="settings-graph-type-dropdown"),
                    dcc.Dropdown(
                        id="settings-graph-type-dropdown",
                        options=graph_selection_list,
                        value=graph_selection_list[0]["value"],
                        clearable=False
                    )
                ]
            )
        ]
        
    