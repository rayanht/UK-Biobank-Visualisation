import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from hierarchy_tree.HierarchyTree import HierarchyTree
from src._constants import MAX_SELECTIONS
from src.dash_app import app
from src.tree.node_utils import get_hierarchy, filter_hierarchy

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
                    dbc.Input(
                        className="mb-1", id="search-input", placeholder="Search"
                    ),
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
