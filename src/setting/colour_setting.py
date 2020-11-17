import dash_core_components as dcc
import dash_html_components as html

from src.graph import ValueType, get_field_type
from src.tree.node_utils import get_field_id, get_option
from src.setting.variable_setting import get_option_dropdown as get_dropdown
from src.setting.variable_setting import get_dropdown_id as get_var_dropdown_id
from dash.dependencies import Input, Output, State
from src.dash_app import app


def get_option_dropdown(arg):
    return html.Div(    
                id="colour-selection-div",
                children=[
                    html.H6("Colour", className="mt-2"),
                    get_dropdown("colour"),
                ],
                style={"display": "none"},
            )

def get_dropdown_id():
    return get_var_dropdown_id("colour")

# Callback for updating colour option visibility
@app.callback(
    Output(component_id="colour-selection-div", component_property="style"),
    Input(component_id="settings-graph-type-dropdown", component_property="value"),
)
def update_colour_visible(graph_type):
    if ((graph_type == 4) | (graph_type == None)):
        # Currently do not support colour for pie charts
        return {"display": "none"}
    return {"display": "block"}

@app.callback(
    Output(component_id=get_dropdown_id(), component_property="options"),
    Input(component_id="tree", component_property="n_updates"),
    State(component_id="tree", component_property="selected_nodes"),
)
def update_dropdown(n, selected_nodes):
    """Update the dropdown when nodes from the tree are selected"""
    options = [get_option(node) for node in selected_nodes if is_colour_option(node)]
    return options

def is_colour_option(node):
    node_value_type = get_field_type(get_field_id(node))
    return (
        node_value_type == ValueType.INTEGER
        or node_value_type == ValueType.CAT_SINGLE
        or node_value_type == ValueType.CAT_MULT
    )