import dash_core_components as dcc
import dash_html_components as html

from src.graph_data import get_field_type
from src.value_type import ValueType
from src.tree.node_utils import get_field_id, get_option
from src.setting.variable_setting import get_option_dropdown as get_dropdown
from src.setting.variable_setting import get_dropdown_id as get_var_dropdown_id
from dash.dependencies import Input, Output, State
from src.dash_app import app


def get_option_dropdown(arg):
    return html.Div(
        id="colour-selection-div",
        children=[html.H6("Colour", className="mt-2"), get_dropdown("colour")],
        style={"display": "none"},
    )


def get_dropdown_id():
    return get_var_dropdown_id("colour")


# Callback for updating colour option visibility
@app.callback(
    [
        Output(component_id="colour-selection-div", component_property="style"),
        Output(component_id=get_dropdown_id(), component_property="options"),
        Output(component_id=get_dropdown_id(), component_property="value"),
    ],
    [
        Input(component_id="settings-graph-type-dropdown", component_property="value"),
        Input(component_id="tree-next-btn", component_property="n_clicks"),
        Input(component_id="settings-collapse-toggle", component_property="n_clicks"),
    ],
    [State(component_id="tree", component_property="selected_nodes")],
)
def update_colour_visible(graph_type, n1, n2, selected_nodes):
    all_options, violin_options = [], []
    for node in selected_nodes:
        option = get_option(node)
        is_all_colour, is_violin_colour = is_colour_option(node)
        if is_all_colour:
            all_options.append(option)
        if is_violin_colour:
            violin_options.append(option)

    if (graph_type == 4) | (graph_type == None):
        # Currently do not support colour for pie charts
        return {"display": "none"}, {}, None
    if graph_type == 1:
        # Only categorical data can be used for violin plot colouring
        return {"display": "block"}, violin_options, None
    return {"display": "block"}, all_options, None


def is_colour_option(node):
    """Returns two boolean values:
        (first) if option can be used for general colouring,
        (second) if option can be used for colouring violin plots"""
    node_value_type = get_field_type(get_field_id(node))
    return (
        (
            node_value_type == ValueType.INTEGER
            or node_value_type == ValueType.CONT
            or node_value_type == ValueType.CAT_SINGLE
            or node_value_type == ValueType.CAT_MULT
        ),
        (
            node_value_type == ValueType.CAT_SINGLE
            or node_value_type == ValueType.CAT_MULT
        ),
    )
