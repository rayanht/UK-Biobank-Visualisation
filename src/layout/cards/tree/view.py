import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from hierarchy_tree.HierarchyTree import HierarchyTree
from src._constants import MAX_SELECTIONS
from src.dash_app import app
from src.tree.node_utils import get_hierarchy, filter_hierarchy

hierarchy, clopen_state = get_hierarchy()

tabs = [
    dbc.Tabs(
        [
            dbc.Tab(tab_id="tree", label="Data Fields"),
            dbc.Tab(tab_id="saved", label="Saved Selections"),
        ],
        id="explore-tabs",
        active_tab="tree",
        card=True,
    )
]

explore_tab_content = {
    "tree": [
        dbc.Input(className="mb-1", id="search-input", placeholder="Search"),
        html.Div(
            [
                HierarchyTree(
                    id="tree",
                    data=hierarchy,
                    selected_nodes=[],
                    max_selections=MAX_SELECTIONS,
                    n_updates=0,
                    clopenState=clopen_state,
                ),
                dbc.Modal(
                    [
                        dbc.ModalHeader("Save this variable selection"),
                        dbc.ModalBody("To be implemented :("),
                        dbc.ModalFooter(
                            dbc.Button("Close", id="close", className="ml-auto")
                        ),
                    ],
                    id="save-selection-modal",
                ),
            ],
            className="flex-grow-1 p-1",
            style={"overflow": "auto"},
        ),
        dbc.Row(
            [
                dbc.Button(
                    "Save selection",
                    id="save-selection-btn",
                    color="secondary",
                    className="ml-3",
                    block=False,
                ),
                dbc.Col(
                    html.Div(
                        style={"textAlign": "right"},
                        id="selections-capacity",
                        className="mt-1",
                    ),
                    align="center",
                ),
                dbc.Button(
                    "Next", id="tree-next-btn", color="primary", className="mr-3"
                ),
            ],
            justify="end",
            className="mt-2",
        ),
    ],
    "saved": html.H6("Your saved selections will appear here. Not implemented :("),
}

layout = dbc.Card(
    [
        html.A(
            dbc.CardHeader(html.H5("Explore", className="ml-1")),
            id="tree-collapse-toggle",
        ),
        dbc.Collapse(
            dbc.CardBody(
                dbc.Card(
                    children=[
                        dbc.CardHeader(tabs),
                        dbc.CardBody(
                            explore_tab_content["tree"],
                            className="d-flex flex-column",
                            style={"height": "41rem"},
                            id="explore-card-body",
                        ),
                    ]
                )
            ),
            id=f"collapse-tree",
            is_open=True,
        ),
    ]
)


@app.callback(
    Output("explore-card-body", "children"), [Input("explore-tabs", "active_tab")]
)
def tab_contents_analysis(tab_id):
    return explore_tab_content[tab_id]


@app.callback(
    [Output("tree", "data"), Output("tree", "clopen_state")],
    [Input("search-input", "value")],
    [State("tree", "clopenState")],
)
def output_text(s, clopen):
    return filter_hierarchy(clopen, s)


@app.callback(
    Output("save-selection-modal", "is_open"),
    [Input("save-selection-btn", "n_clicks"), Input("close", "n_clicks")],
    [State("save-selection-modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open
