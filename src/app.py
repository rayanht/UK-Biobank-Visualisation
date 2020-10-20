# -*- coding: utf-8 -*-

# Run this app with `gunicorn app:server` and
# visit http://127.0.0.1:8000/ in your web browser.
import os
import sys

import dash

from src.graph import get_field_plot
from src.tree.node_utils import get_hierarchy, filter_hierarchy

sys.path.append(os.path.join(os.path.dirname(__file__), 'hierarchy_tree'))

from hierarchy_tree.HierarchyTree import HierarchyTree
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

app.title = "UK BioBank Explorer"

colors = {
    'background': "#fdfdfd",
    'text': "#7FDBFF",
    'navbar-bg': "#f7f7f7",
}

hierarchy, clopen_state = get_hierarchy()

navbar = dbc.Navbar(
    [
        dbc.NavbarBrand("UK BioBank Explorer", href="#"),
        dbc.NavbarToggler(id="navbar-toggler"),
        dbc.Collapse(
            dbc.Nav(
                [
                    dbc.NavItem(dbc.NavLink("Graphs", href="#")),  # dummy graphs link
                    dbc.DropdownMenu(  # dummy dropdown menu
                        children=[
                            dbc.DropdownMenuItem("Entry 1"),
                            dbc.DropdownMenuItem("Entry 2"),
                            dbc.DropdownMenuItem(divider=True),
                            dbc.DropdownMenuItem("Entry 3"),
                        ],
                        nav=True,
                        in_navbar=True,
                        label="Menu",
                        right=True
                    )
                ], className="ml-auto", navbar=True
            ),
            id="navbar-collapse",
            navbar=True,
        ),
    ],
    className="px-5"
)

treeCard = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H4("Explore", className="tree-card-title"),
                dbc.Input(id="search-input", value="Search"),
                HierarchyTree(id='tree', data=hierarchy, selected=[], n_updates=0, clopenState=clopen_state),
            ]
        ),
    ],
    style={"minHeight": "45rem"},  # for dummy purposes, to remove later
)

settingsCard = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H4("Settings", className="settings-card-title"),
                dbc.Label("Graph Type", html_for="settings-graph-type-dropdown"),
                dcc.Dropdown(
                    id="settings-graph-type-dropdown",
                    options=[
                        {"label": "Violin", "value": 1},
                        {"label": "Scatter", "value": 2},
                        {"label": "Bar", "value": 3},
                    ],
                    value=2,
                    clearable=False
                )
            ]
        ),
    ],
    style={"minHeight": "40rem"},  # for dummy purposes, to remove later
)

graphsCard = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H4("Plot", className="graphs-card-title"),
                dcc.Graph(id='graph', )
            ]
        ),
    ],
    style={"minHeight": "47rem"},  # for dummy purposes, to remove later
)

app.layout = html.Div(
    style={'backgroundColor': colors['background'], 'height': "100vh"},
    children=
    [
        navbar,
        # row,
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            treeCard,  # Container for tree
                            width=4,
                        ),
                        dbc.Col(
                            settingsCard,  # Container for settings
                            width=2,
                        ),
                        dbc.Col(
                            graphsCard,  # Container for graphs
                            width=6,
                        ),
                    ]
                )
            ],
            className="p-5",
            fluid=True
        )
    ]
)


# we use a callback to toggle the collapse on small screens


@app.callback([Output("tree", "data"), Output("tree", "clopen_state")], [Input("search-input", "value")],
              [State("tree", "clopenState")])
def output_text(s, clopen):
    return filter_hierarchy(clopen, s)


@app.callback(Output("navbar-collapse", "is_open"), [Input("navbar-toggler", "n_clicks")],
              [State("navbar-collapse", "is_open")])
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output(component_id='graph', component_property='figure'),
    [Input(component_id='tree', component_property='n_updates')],
    [State(component_id='tree', component_property='selected')]
)
def update_graph(n, selected):
    if len(selected) == 0:
        return {
            "layout": {
                "xaxis": {
                    "visible": False
                },
                "yaxis": {
                    "visible": False
                },
                "annotations": [
                    {
                        "text": "Select a data category to begin",
                        "xref": "paper",
                        "yref": "paper",
                        "showarrow": False,
                        "font": {
                            "size": 22
                        }
                    }
                ]
            }
        }
    return get_field_plot(selected[0])  # Plot first selected data
