import dash_core_components as dcc

from dash.dependencies import Input, MATCH, Output, State
from src.dash_app import app
from src.tree.node_utils import get_option
from src._constants import MAX_SELECTIONS


def get_option_dropdown(var: str):
    return dcc.Dropdown(
        id={"var": var, "type": "variable-dropdown"},
        options=[],
        placeholder="Select a variable to plot",
        optionHeight=45,
        disabled= (var == 'y'),
    )


def get_dropdown_id(var=MATCH):
    return {"var": var, "type": "variable-dropdown"}


@app.callback(
    [
        Output(component_id="selections-capacity", component_property="children"),
        Output(component_id=get_dropdown_id('x'), component_property="options"),
        Output(component_id=get_dropdown_id('y'), component_property="options"),
        Output(component_id=get_dropdown_id('all'), component_property="options"),
    ],
    [Input(component_id="tree", component_property="n_updates")],
    [State(component_id="tree", component_property="selected_nodes")],
)
def update_dropdown(n, selected_nodes):
    """Update the dropdown when nodes from the tree are selected"""
    options = [get_option(node) for node in selected_nodes]
    return (
        f"{len(options)}/{MAX_SELECTIONS} variables selected",
        options,
        options,
        options,
    )


@app.callback(
    Output(component_id=get_dropdown_id("y"), component_property="disabled"),
    Input(component_id=get_dropdown_id("x"), component_property="value"),
)
def update_y_axis_disabled(x_value):
    if not x_value:
        return True
    return False
