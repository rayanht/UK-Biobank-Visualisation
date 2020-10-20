# -*- coding: utf-8 -*-

# Run this app with `gunicorn app:server` and
# visit http://127.0.0.1:8000/ in your web browser.
import os
import re
import sys
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from src.graph import get_field_plot
from src.tree.node_utils import get_hierarchy, filter_hierarchy
from dash.dependencies import Input, Output, State

sys.path.append(os.path.join(os.path.dirname(__file__), 'hierarchy_tree'))
from hierarchy_tree.HierarchyTree import HierarchyTree


app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

app.title = "UK BioBank Explorer"

colors = {
    'background': "#fdfdfd",
    'text': "#7FDBFF",
    'navbar-bg': "#f7f7f7",
}

hierarchy, clopen_state = get_hierarchy()

MAX_SELECTIONS = 30

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
                html.H4("Explore", style={"margin-bottom": "20px"}, className="tree-card-title"),
                dbc.Input(style={"margin-bottom": "5px"}, id="search-input", value="Search"),
                HierarchyTree(id='tree', data=hierarchy, selected_nodes=[], max_selections=MAX_SELECTIONS,
                              n_updates=0, clopenState=clopen_state),
                html.Div(style={"margin-top": "2px", 'textAlign': 'right'}, id='selections-capacity')
            ]
        ),
    ],
    style={"minHeight": "45rem"},  # for dummy purposes, to remove later
)

settingsCard = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H4("Settings", style={"margin-bottom": "20px"}, className="settings-card-title"),
                html.H5("X-axis"),
                dcc.Dropdown(
                    id='variable-dropdown-x',
                    options=[],
                    placeholder="Select a variable to plot",
                    optionHeight=45
                ),

                html.H5("Y-axis", style={"margin-top": "15px"}),
                dcc.Dropdown(
                    id='variable-dropdown-y',
                    options=[],
                    placeholder="Select a variable to plot",
                    optionHeight=45,
                    # TODO: remove this when we are able to plot 2 variables at once (i.e. enable second variable)
                    disabled=True
                ),
            ]
        ),
    ],
    style={"minHeight": "40rem"},  # for dummy purposes, to remove later
)

graphsCard = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H4("Plot", style={"margin-bottom": "20px"}, className="graphs-card-title"),
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
    [Output(component_id='variable-dropdown-x', component_property='options'),
     Output(component_id='selections-capacity', component_property='children'),
     Output(component_id='variable-dropdown-y', component_property='options')],
    [Input(component_id='tree', component_property='n_updates')],
    [State(component_id='tree', component_property='selected_nodes')]
)
def update_dropdown(n, selected_nodes):
    """Update the dropdown when nodes from the tree are selected"""
    def get_option(node):
        label = node['label']
        title = None
        if '(' in label:
            title = label
            label = re.sub(r'\([^)]*\)', '', label)
        return {'label': label, 'value': node['field_id'], 'title': title}

    options = [get_option(node) for node in selected_nodes]
    return options, f"{len(options)}/{MAX_SELECTIONS} variables selected", options


@app.callback(
    Output(component_id='graph', component_property='figure'),
    [Input('variable-dropdown-x', 'value')])
def update_graph(value):
    """Update the graph when the dropdown selection changes"""
    if value is None:
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
    return get_field_plot(value)
