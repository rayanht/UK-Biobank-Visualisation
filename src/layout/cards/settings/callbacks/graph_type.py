import dash_core_components as dcc
from src.dash_app import app

from dash.dependencies import Input, Output
from src.graph_data import get_field_type
from src.value_type import ValueType
from .variable_selection import get_dropdown_id as get_var_dropdown_id


def get_option_dropdown(arg=None):
    return dcc.Dropdown(
        id="settings-graph-type-dropdown",
        options=[],
        placeholder="Select a graph type",
        clearable=False,
        disabled=True,
    )


@app.callback(
    [
        Output(
            component_id="settings-graph-type-dropdown", component_property="options"
        ),
        Output(component_id="settings-graph-type-dropdown", component_property="value"),
        Output(
            component_id="settings-graph-type-dropdown", component_property="disabled"
        ),
        Output(
            component_id="settings-graph-type-dropdown",
            component_property="placeholder",
        ),
    ],
    [
        Input(component_id=get_var_dropdown_id("x"), component_property="value"),
        Input(component_id=get_var_dropdown_id("y"), component_property="value"),
    ],
)
def update_graph_type(variable_dropdown_x, variable_dropdown_y):
    """Update the dropdown when nodes from the tree are selected"""

    options = {
        "violin": {"label": "Violin", "value": 1},
        "scatter": {"label": "Scatter", "value": 2},
        "bar": {"label": "Bar", "value": 3},
        "pie": {"label": "Pie", "value": 4},
        # "box": {"label": "Box", "value": 5,},
    }

    if variable_dropdown_x is None:
        return [], None, True, "Select a graph type"

    graph_selection_list = []

    if variable_dropdown_y is None:
        # Only one variable selected
        field_id = variable_dropdown_x
        value_type = get_field_type(str(field_id))

        supported_graphs = value_type.supported_graphs

        for option_key in options:
            option = options[option_key]
            graph_type = option["value"]
            if graph_type in supported_graphs:
                graph_selection_list.append(option)

    else:
        # Both variables selected
        # Logic is:
        # If the x-axis variable is continuous, integer, date or time:
        #   If the y-axis variable is continuous or integer:
        #       You can use scatter plot
        # Else if x-axis variable is categorical:
        #   If the y-axis variable is continuous or integer:
        #       You can use violin plot, box plot
        x_value_type = get_field_type(str(variable_dropdown_x))
        y_value_type = get_field_type(str(variable_dropdown_y))

        if (
            x_value_type == ValueType.INTEGER
            or x_value_type == ValueType.CONT
            or x_value_type == ValueType.DATE
            or x_value_type == ValueType.TIME
        ):
            if y_value_type == ValueType.INTEGER or y_value_type == ValueType.CONT:
                graph_selection_list.append(options["scatter"])

        elif x_value_type == ValueType.CAT_SINGLE or x_value_type == ValueType.CAT_MULT:
            if y_value_type == ValueType.INTEGER or y_value_type == ValueType.CONT:
                # graph_selection_list.append(options["box"])
                graph_selection_list.append(options["violin"])

    if len(graph_selection_list) == 0:
        return graph_selection_list, None, True, "No supported graph types"

    return (
        graph_selection_list,
        graph_selection_list[0]["value"],
        False,
        "Select a graph type",
    )
