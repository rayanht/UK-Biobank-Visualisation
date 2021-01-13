import dash_html_components as html
from dash.dependencies import Input, Output, State

from src.dash_app import app
from src.graph_data import get_field_type
from src.tree.node_utils import get_field_id, get_option
from src.value_type import ValueType
from .variable_selection import (
    get_dropdown_id as get_var_dropdown_id,
    get_option_dropdown as get_dropdown,
)


def get_option_dropdown(arg):
    return html.Div(
        id="colour-selection-div",
        children=[html.H6("Colour", className="mt-2"), get_dropdown("colour")],
        style={"display": "none"},
    )


def get_dropdown_id():
    return get_var_dropdown_id("colour")


@app.callback(
    [
        Output(component_id="colour-selection-div", component_property="style"),
        Output(component_id=get_dropdown_id(), component_property="options"),
        Output(component_id=get_dropdown_id(), component_property="value"),
    ],
    [Input(component_id="settings-graph-type-dropdown", component_property="value")],
    [State(component_id="tree", component_property="selected_nodes")],
)
def update_colour_visible(graph_type, selected_nodes):
    """
    Callback to update the visibility of the colour dropdown

    :param graph_type: the type of graph that is currently being prepared.
                       (Violin, Pie, Scatter etc.)
    :param selected_nodes: the data fields that are currently selected in the
                           tree
    :return: a HTML div of the colour dropdown, potentially hidden.
    """
    all_options, violin_options = [], []
    for node in selected_nodes:
        option = get_option(node)
        is_all_colour, is_violin_colour = is_colour_option(node)
        if is_all_colour:
            all_options.append(option)
        if is_violin_colour:
            violin_options.append(option)

    if (graph_type == 4) | (graph_type is None):
        # Currently do not support colour for pie charts
        return {"display": "none"}, {}, None
    if graph_type == 1:
        # Only categorical data can be used for violin plot colouring
        return {"display": "block"}, violin_options, None
    return {"display": "block"}, all_options, None


def is_colour_option(node):
    """
    Determine whether or node a data field can be used to colour a plot.

    :param node: the selected data field.
    :return: Tuple(iff option can be used for general colouring,
                  iff option can be used for colouring violin plots)
    """
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
