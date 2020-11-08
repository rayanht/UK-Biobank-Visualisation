import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from src.graph import get_field_plot, get_two_field_plot, ValueType, get_inst_names_options, graph
from src.tree.node_utils import get_option
from dash.dependencies import Input, Output, State
from src.dataset_gateway import field_id_meta_data

from src.dash_app import app

layout = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H4("Settings", className="mb-3 settings-card-title"),
                html.Div(
                    [
                        html.H5("X-axis"),
                        html.H6("Variable"),
                        dcc.Dropdown(
                            id="variable-dropdown-x",
                            options=[],
                            placeholder="Select a variable to plot",
                            optionHeight=45,
                        ),
                        html.Div(
                            id="x-instance-selection-div",
                            children=[
                                html.H6("Instance"),
                                dcc.Dropdown(
                                    id="x-instance-options",
                                    options=[],
                                    placeholder="Select an instance",
                                    optionHeight=70,
                                ),
                            ],
                            style={"display": "none"},
                            className="mt-2",
                        ),
                        html.H5("Y-axis", className="mt-3"),
                        html.H6("Variable"),
                        dcc.Dropdown(
                            id="variable-dropdown-y",
                            options=[],
                            placeholder="Select a variable to plot",
                            optionHeight=45,
                            disabled=True,
                        ),
                        html.Div(
                            id="y-instance-selection-div",
                            children=[
                                html.H6("Instance"),
                                dcc.Dropdown(
                                    id="y-instance-options",
                                    options=[],
                                    placeholder="Select an instance",
                                    optionHeight=70,
                                ),
                            ],
                            style={"display": "none"},
                            className="mt-2",
                        ),
                        html.Div(    
                            id="colour-selection-div",
                            children=[
                                html.H6("Colour"),
                                dcc.Dropdown(
                                    id="settings-graph-colour-dropdown",
                                    options=[],
                                    placeholder="Optional: Group data by category",
                                    clearable=True,
                                    optionHeight=70,
                                ),
                            ],
                            style={"display": "none"},
                            className="mt-2"
                        ),
                        html.H5("Graph Type", className="mt-3"),
                        dcc.Dropdown(
                            id="settings-graph-type-dropdown",
                            options=[],
                            placeholder="Select a graph type",
                            clearable=False,
                            disabled=True,
                        ),
                    ],
                    className="flex-grow-1",
                    style={"overflow": "auto"},
                ),
                dbc.Button(
                    "Plot graph",
                    id="settings-card-submit",
                    color="primary",
                    className="mt-2",
                ),
            ],
            className="d-flex flex-column",
        )
    ],
    style={"height": "50rem"},  # for dummy purposes, to remove later
)

# For getting colour options
@app.callback(
    [
        Output(component_id="colour-selection-div", component_property="style"),
        Output(component_id="settings-graph-colour-dropdown", component_property="options"),
        Output(component_id="settings-graph-colour-dropdown", component_property="value"),
    ],
    [
        Input(component_id="tree", component_property="data"),
        Input(component_id="settings-graph-type-dropdown", component_property="value"),
    ],
)
def get_baseline_nodes(hierarchy, graph_type):
    """Updates colour options with baselines characteristic nodes after tree has been loaded"""
    if ((graph_type == 4) | (graph_type == None)):
        # Currently do not support colour for pie charts
        return {"display": "none"}, [], None
    
    baseline_children = hierarchy[0]['childNodes'][0]['childNodes']
    leaf_baseline = [child for child in baseline_children if isLeaf(child)]
    options = [get_option(node) for node in leaf_baseline]
    if (graph_type == 1):
        # Violin plot can only use Sex as colour argument
        options = [option for option in options if is_sex_option(option)]
    return {"display": "block"}, options, None

def isLeaf(node):
    """Returns true if node is a leaf"""
    try:
        return not node['hasCaret']
    except KeyError:
        return True;

def is_sex_option(option):
    return option['value'] == '31'

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
    [Input(component_id="variable-dropdown-x", component_property="value")],
    Input(component_id="variable-dropdown-y", component_property="value"),
)
def update_graph_type(variable_dropdown_x, variable_dropdown_y):
    """Update the dropdown when nodes from the tree are selected"""

    options = {
        "violin": {"label": "Violin", "value": 1},
        "scatter": {"label": "Scatter", "value": 2},
        "bar": {"label": "Bar", "value": 3},
        "pie": {"label": "Pie", "value": 4},
        "box": {"label": "Box", "value": 5},
    }

    if variable_dropdown_x is None:
        return [], None, True, "Select a graph type"

    graph_selection_list = []

    if variable_dropdown_y is None:
        # Only one variable selected
        field_id = variable_dropdown_x

        df = field_id_meta_data()
        value_type_id = int(
            df.loc[df["field_id"] == str(field_id)]["value_type"].values[0]
        )
        value_type = ValueType(value_type_id)

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

        df = field_id_meta_data()
        x_value_type_id = int(
            df.loc[df["field_id"] == str(variable_dropdown_x)]["value_type"].values[0]
        )
        x_value_type = ValueType(x_value_type_id)

        y_value_type_id = int(
            df.loc[df["field_id"] == str(variable_dropdown_y)]["value_type"].values[0]
        )
        y_value_type = ValueType(y_value_type_id)

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
                graph_selection_list.append(options["box"])
                graph_selection_list.append(options["violin"])

    if len(graph_selection_list) == 0:
        return graph_selection_list, None, True, "No supported graph types"

    return (
        graph_selection_list,
        graph_selection_list[0]["value"],
        False,
        "Select a graph type",
    )


@app.callback(
    [
        Output(component_id="variable-dropdown-y", component_property="disabled"),
        Output(component_id="variable-dropdown-y", component_property="value"),
    ],
    [Input(component_id="variable-dropdown-x", component_property="value")],
    [State(component_id="variable-dropdown-y", component_property="value")],
)
def update_y_axis_disabled(x_value, y_value):
    if not x_value:
        return True, None
    return False, y_value


# for instance selection
@app.callback(
    [
        Output(component_id="x-instance-selection-div", component_property="style"),
        Output(component_id="x-instance-options", component_property="options"),
        Output(component_id="x-instance-options", component_property="value"),
    ],
    [Input(component_id="variable-dropdown-x", component_property="value")],
)
def update_x_sel_inst(x_value):
    """Updating list of instances that may be selected on x-axis"""
    if not x_value:
        return {"display": "none"}, [], ""

    dict_with_inst = get_inst_names_options(x_value, False)
    options = [
        {
            "label": prune_instance_label(dict_with_inst[field_inst_id]),
            "value": field_inst_id,
        }
        for field_inst_id in dict_with_inst
    ]

    div_visible = {"display": "block"} if len(options) != 1 else {"display": "none"}

    return div_visible, options, options[0]["value"]  # select first instance by default


def prune_instance_label(label):
    # deletes everything after the year, which ends in a close parenthesis
    sep = ")"
    return label.split(sep, 1)[0] + sep


@app.callback(
    [
        Output(component_id="y-instance-selection-div", component_property="style"),
        Output(component_id="y-instance-options", component_property="options"),
        Output(component_id="y-instance-options", component_property="value"),
    ],
    [Input(component_id="variable-dropdown-y", component_property="value")],
)
def update_y_sel_inst(y_value):
    """Updating list of instances that may be selected on y-axis"""
    if not y_value:
        return {"display": "none"}, [], ""

    dict_with_inst = get_inst_names_options(y_value, False)
    options = [
        {
            "label": prune_instance_label(dict_with_inst[field_inst_id]),
            "value": field_inst_id,
        }
        for field_inst_id in dict_with_inst
    ]

    div_visible = {"display": "block"} if len(options) != 1 else {"display": "none"}

    return div_visible, options, options[0]["value"]  # select first instance by default


# for plotting graph
@app.callback(
    Output(component_id="graph", component_property="figure"),
    [Input(component_id="settings-card-submit", component_property="n_clicks")],
    [
        State(component_id="settings-graph-type-dropdown", component_property="value"),
        State(component_id="x-instance-options", component_property="value"),
        State(component_id="y-instance-options", component_property="value"),
        State(component_id="settings-graph-colour-dropdown", component_property="value")
    ],
)
def update_graph(n, graph_type, x_value, y_value, colour):
    """Update the graph when the plot button is pressed"""
    if not x_value:
        return {
            "layout": {
                "xaxis": {"visible": False},
                "yaxis": {"visible": False},
                "annotations": [
                    {
                        "text": "No data plotted",
                        "xref": "paper",
                        "yref": "paper",
                        "showarrow": False,
                        "font": {"size": 22},
                    }
                ],
            }
        }
    if not y_value:
        return get_field_plot(x_value, graph_type, colour)  # Plot first selected data
    return get_two_field_plot(x_value, y_value, graph_type, colour)
