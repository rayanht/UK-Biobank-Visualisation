import os
import re
import sys
import dash_html_components as html
import dash_bootstrap_components as dbc
from src.tree.node_utils import get_hierarchy, filter_hierarchy, get_option
from dash.dependencies import Input, Output, State

sys.path.append(os.path.join(os.path.dirname(__file__), "hierarchy_tree"))
from hierarchy_tree.HierarchyTree import HierarchyTree

from src.dash_app import app

MAX_SELECTIONS = 30

hierarchy, clopen_state = get_hierarchy()

layout = dbc.Card(
    [
        html.A(
            dbc.CardHeader(html.H5("Explore", className="ml-1")),
            id="tree-collapse-toggle",
        ),
        dbc.Collapse(
            dbc.CardBody(
                [
                    # html.H4("Explore", className="mb-3 tree-card-title"),
                    dbc.Input(className="mb-1", id="search-input", value="Search"),
                    html.Div(
                        [
                            HierarchyTree(
                                id="tree",
                                data=hierarchy,
                                selected_nodes=[],
                                max_selections=MAX_SELECTIONS,
                                n_updates=0,
                                clopenState=clopen_state,
                            )
                        ],
                        className="flex-grow-1 p-1",
                        style={"overflow": "auto"},
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Div(
                                    style={"textAlign": "right"},
                                    id="selections-capacity",
                                    className="mt-1",
                                ),
                                align="center",
                            ),
                            dbc.Button(
                                "Next",
                                id="tree-next-btn",
                                color="primary",
                                className="mr-3",
                            ),
                        ],
                        justify="end",
                        className="mt-2",
                    ),
                ],
                className="d-flex flex-column",
                style={"height": "41rem"},
            ),
            id=f"collapse-tree",
            is_open=True,
        ),
    ]
)


@app.callback(
    [Output("tree", "data"), Output("tree", "clopen_state")],
    [Input("search-input", "value")],
    [State("tree", "clopenState")],
)
def output_text(s, clopen):
    return filter_hierarchy(clopen, s)


@app.callback(
    [
        Output(component_id="variable-dropdown-x", component_property="options"),
        Output(component_id="selections-capacity", component_property="children"),
        Output(component_id="variable-dropdown-y", component_property="options"),
    ],
    [Input(component_id="tree", component_property="n_updates")],
    [State(component_id="tree", component_property="selected_nodes")],
)
def update_dropdown(n, selected_nodes):
    """Update the dropdown when nodes from the tree are selected"""
    options = [get_option(node) for node in selected_nodes]
    return options, f"{len(options)}/{MAX_SELECTIONS} variables selected", options

