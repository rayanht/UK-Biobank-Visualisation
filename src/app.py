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

from src.dataset_gateway import MetaDataLoader
from src.graph import ValueType

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

app.title = "UK BioBank Explorer"

colors = {
    'background': "#fdfdfd",
    'text': "#7FDBFF",
    'navbar-bg': "#f7f7f7",
}

hierarchy, clopen_state = get_hierarchy()

mt = MetaDataLoader()

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
                html.H4("Explore", className="mb-3 tree-card-title"),
                html.Div([
                    dbc.Input(className="mb-1", id="search-input", value="Search"),
                    HierarchyTree(id='tree', data=hierarchy, selected_nodes=[], max_selections=MAX_SELECTIONS,
                                n_updates=0, clopenState=clopen_state),
                ], className="flex-grow-1 p-1", style={"overflow": "auto"}),
                html.Div(style={'textAlign': 'right'}, id='selections-capacity', className="mt-1")
            ], className="d-flex flex-column"
        ),
    ],
    style={"height": "50rem"},  # for dummy purposes, to remove later
)

# settingsCard = dbc.Card(id='settings-card', 
settingsCard = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H4("Settings", className="mb-3 settings-card-title"),
                html.Div([
                    html.H5("X-axis"),
                    dcc.Dropdown(
                        id='variable-dropdown-x',
                        options=[],
                        placeholder="Select a variable to plot",
                        optionHeight=45
                    ),
                    html.H5("Y-axis", className="mt-2"),
                    dcc.Dropdown(
                        id='variable-dropdown-y',
                        options=[],
                        placeholder="Select a variable to plot",
                        optionHeight=45,
                        # TODO: remove this when we are able to plot 2 variables at once (i.e. enable second variable)
                        disabled=True
                    ),
                    html.H5("Graph Type", className="mt-2"),
                    dcc.Dropdown(
                        id="settings-graph-type-dropdown",
                        options=[],
                        # value=graph_selection_list[0]["value"],
                        placeholder="Select a graph type",
                        clearable=False,
                        disabled=True
                    )
                ], className="flex-grow-1", style={"overflow": "auto"}),
                dbc.Button("Plot graph", id="settings-card-submit", color="primary", className="mt-2"),
            ]
        , className="d-flex flex-column"),
    ],
    style={"height": "50rem"},  # for dummy purposes, to remove later
)

graphsCard = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H4("Plot", className="mb-3 graphs-card-title"),
                dcc.Graph(id='graph', )
            ]
        ),
    ],
    style={"minHeight": "50rem"},  # for dummy purposes, to remove later
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
            style={"padding": "2.5rem 3rem 0rem 3rem"},
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
    [Output(component_id='settings-graph-type-dropdown', component_property='options'),
     Output(component_id='settings-graph-type-dropdown', component_property='value'),
     Output(component_id='settings-graph-type-dropdown', component_property='disabled')],
    [Input(component_id='variable-dropdown-x', component_property='value')]
)
def update_graph_type(variable_dropdown_x):
    """Update the dropdown when nodes from the tree are selected"""
    if (variable_dropdown_x is None): 
        return [], None, True

    field_id = variable_dropdown_x # Only supports one variable for now

    df = mt.field_id_meta_data
    value_type_id = int(df.loc[df['field_id'] == str(field_id)]['value_type'].values[0])
    value_type = ValueType(value_type_id)

    options = [
        {"label": "Violin", "value": 1},
        {"label": "Scatter", "value": 2},
        {"label": "Bar", "value": 3, "disabled": True},
        {"label": "Pie", "value": 4, "disabled": True},
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

    return graph_selection_list, graph_selection_list[0]["value"], False

@app.callback(
    Output(component_id='graph', component_property='figure'),
    [Input(component_id='settings-card-submit', component_property='n_clicks')],
    [State(component_id='variable-dropdown-x', component_property='value'),
    State(component_id='settings-graph-type-dropdown', component_property='value')])
def update_graph(n, x_value, graph_type):
    """Update the graph when the dropdown selection changes"""
    if x_value is None:
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
    return get_field_plot(x_value, graph_type)  # Plot first selected data

# app.callback(
#     Output(component_id='settings-card', component_property='children'),
#     [Input(component_id='tree', component_property='n_updates')],
#     [State(component_id='tree', component_property='selected')]
#     )(update_settings_card)
