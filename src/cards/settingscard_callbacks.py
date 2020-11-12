from dash.dependencies import Input, Output, State

from src.dash_app import dash, app

from src.dataset_gateway import DatasetGateway, Query, field_id_meta_data
from src.graph import (
    filter_data,
    get_field_plot,
    get_statistics,
    get_inst_names_options,
    prune_data,
    ValueType,
)
from src.dash_app import app
import pandas as pd
from src.tree.node import NodeIdentifier


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
    return get_updated_instances(x_value)


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
    return get_updated_instances(y_value)


def prune_instance_label(label):
    # deletes everything after the year, which ends in a close parenthesis
    sep = ")"
    return label.split(sep, 1)[0] + sep


def get_updated_instances(value):
    """Updating list of instances that may be selected"""
    if not value:
        return {"display": "none"}, [], ""

    dict_with_inst = get_inst_names_options(value)
    options = [
        {
            "label": prune_instance_label(dict_with_inst[field_inst_id]),
            "value": field_inst_id,
        }
        for field_inst_id in dict_with_inst
    ]

    div_visible = {"display": "block"} if len(options) != 1 else {"display": "none"}

    return div_visible, options, options[0]["value"]  # select first instance by default


# update options (possibly merge with apply_graph_settings to prevent sending cached_data twice?)
@app.callback(
    [
        # x slider
        Output(component_id="x-filter-slider", component_property="min"),
        Output(component_id="x-filter-slider", component_property="max"),
        Output(component_id="x-filter-slider", component_property="value"),
        Output(component_id="x-filter-slider", component_property="marks"),
        Output(component_id="x-filter-slider-div", component_property="style"),
        # y slider
        Output(component_id="y-filter-slider", component_property="min"),
        Output(component_id="y-filter-slider", component_property="max"),
        Output(component_id="y-filter-slider", component_property="value"),
        Output(component_id="y-filter-slider", component_property="marks"),
        Output(component_id="y-filter-slider-div", component_property="style"),
    ],
    [
        Input(component_id="graph-data", component_property="data"),
        Input(component_id="x-instance-options", component_property="value"),
        Input(component_id="y-instance-options", component_property="value"),
    ],
)
def update_settings_options(cached_data, x_value, y_value):
    x_filter_tuple = y_filter_tuple = (
        dash.no_update,
        dash.no_update,
        None,
        dash.no_update,
        dash.no_update,
    )

    if not cached_data:
        return x_filter_tuple + y_filter_tuple

    filtered_data = pd.read_json(cached_data["data"], orient="split")

    # update x-axis settings
    if cached_data["x-value"] != "":
        x_filter_tuple = get_range_slider_tuple(
            filtered_data, x_value, cached_data["x-value"]
        )

    # update y-axis settings
    if cached_data["y-value"] != "":
        y_filter_tuple = get_range_slider_tuple(
            filtered_data, y_value, cached_data["y-value"]
        )

    return x_filter_tuple + y_filter_tuple


def get_range_slider_tuple(filtered_data, curr_value, stored_value):
    if stored_value != curr_value:
        return (
            dash.no_update,
            dash.no_update,
            None,
            dash.no_update,
            {"display": "none"},
        )
    node_id = NodeIdentifier(stored_value)
    df = filtered_data[node_id.db_id()]
    df_min = int(df.min())
    df_max = int(df.max())
    return (
        df_min,
        df_max,
        [df_min, df_max],
        {df_min: str(df_min), df_max: str(df_max)},
        {"display": "block"},
    )


# store x_value and y_value too in the dcc.store,
# if not the same as current selected ones, then no_update. it will be called again once the store is updated with new and correct data
# if the same, then update using the settings
# this makes it faster for changing settings without having to query database again
@app.callback(
    [
        Output(component_id="graph-data", component_property="data"),
        Output(component_id="plotted-data", component_property="data"),
        Output(component_id="graph", component_property="figure"),
        Output(component_id="statistics", component_property="children"),
        Output(component_id="download-btn", component_property="disabled"),
    ],
    [Input(component_id="settings-card-submit", component_property="n_clicks")],
    [
        State(component_id="graph-data", component_property="data"),
        State(component_id="x-instance-options", component_property="value"),
        State(component_id="y-instance-options", component_property="value"),
        State(component_id="settings-graph-type-dropdown", component_property="value"),
        # filters
        State(component_id="x-filter-slider", component_property="value"),
        State(component_id="y-filter-slider", component_property="value"),
    ],
)
def get_data(n, cached_data, x_value, y_value, graph_type, x_filter, y_filter):
    new_cached_data = dash.no_update
    data = None
    node_id_y = None
    # get new data if cached data is outdated
    if (
        not cached_data
        or cached_data["x-value"] != x_value
        or cached_data["y-value"] != y_value
    ):
        if not x_value:
            new_cached_data = None
            data = None
        else:
            node_id_x = NodeIdentifier(x_value)
            if not y_value:
                data = prune_data(
                    DatasetGateway.submit(Query.from_identifier(node_id_x))
                )
                new_cached_data = {
                    "x-value": x_value,
                    "y-value": "",
                    "data": data.to_json(date_format="iso", orient="split"),
                }
                print("Getting new data!")
            else:
                node_id_y = NodeIdentifier(y_value)
                data = prune_data(
                    DatasetGateway.submit(
                        Query.from_identifiers([node_id_x, node_id_y])
                    )
                )
                new_cached_data = {
                    "x-value": x_value,
                    "y-value": y_value,
                    "data": data.to_json(date_format="iso", orient="split"),
                }
                print("Getting new data!")
    # if cache data is not outdated, use it
    else:
        print(
            f"using cached data for {cached_data['x-value']} and {cached_data['y-value']}, current x is {x_value} y is {y_value}"
        )
        data = pd.read_json(cached_data["data"], orient="split")

    if data is None:
        return (
            new_cached_data,
            None,
            {
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
            },
            "No data to display",
            True,
        )

    # filter data
    filtered_data = filter_data(data, x_value, y_value, x_filter, y_filter)
    plotted_data_json = filtered_data.to_json(date_format="iso", orient="split")

    removed_eids = filtered_data.loc[:, filtered_data.columns != "eid"]

    return (
        new_cached_data,
        plotted_data_json,
        get_field_plot(removed_eids, x_value, y_value, graph_type),
        get_statistics(removed_eids, x_value, node_id_x, y_value, node_id_y),
        False,
    )
