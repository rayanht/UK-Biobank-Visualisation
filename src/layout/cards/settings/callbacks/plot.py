import inspect
import json
import time

import pandas as pd
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from src.dash_app import dash, app

from src.dataset_gateway import DatasetGateway, Query
from src.graph_data import get_statistics, prune_data, largest_triangle_three_buckets
from src.graph import get_field_plot
from src.tree.node import NodeIdentifier

# Functions to get ids of components
from .instance_selection import get_dropdown_id as get_inst_dropdown_id
from .range_filter import get_slider_id


def get_button(var=None):
    return dbc.Button(
        "Plot graph", id="settings-card-submit", color="primary", className="mt-2"
    )


@app.callback(
    [
        Output(component_id="statistics", component_property="children"),
        Output(component_id="graph", component_property="data"),
        Output(component_id="graph", component_property="figure"),
        Output(component_id="download-btn", component_property="disabled"),
        Output(component_id="loading-metadata-target", component_property="children"),
    ],
    [
        Input(component_id="graph", component_property="selectedData"),
        Input(component_id="settings-card-submit", component_property="n_clicks"),
    ],
    [
        State(component_id="graph", component_property="data"),
        State(component_id=get_inst_dropdown_id("x"), component_property="value"),
        State(component_id=get_inst_dropdown_id("y"), component_property="value"),
        State(component_id="settings-graph-type-dropdown", component_property="value"),
        # Trendline
        State(component_id="trendline-dropdown", component_property="value"),
        # Colour
        State(component_id=get_inst_dropdown_id("colour"), component_property="value"),
        # Filters
        State(component_id=get_slider_id("x"), component_property="value"),
        State(component_id=get_slider_id("y"), component_property="value"),
    ],
)
def get_data(
    selected_data,
    n,
    current_data,
    x_value,
    y_value,
    graph_type,
    trendline,
    colour,
    x_filter,
    y_filter,
):
    """
    Monolithic callback to handle all aspects of displaying data plots.

    :param selected_data: data selected on the current plot. Initially None,
                          is by default the whole graph when first plotted,
                          can be modified by using the lasso tool for example.
    :param n: number of times the `plot` button was clicked.
    :param current_data: data of the current plot. Superset of @selected_data.
    :param x_value: data field in the X Axis.
    :param y_value: data field in the Y Axis.
    :param graph_type: one of {Violin, Pie, Scatter etc.}.
    :param trendline: optional one of {linear, non-linear, None}.
    :param colour: optional colouring parameter, used for data grouping.
    :param x_filter: optional range filter on the value of X.
    :param y_filter: optional range filter on the value of Y.
    """
    ctx = dash.callback_context

    graph_data_update = dash.no_update
    statistics_update = dash.no_update
    loading_bar_update = dash.no_update
    plotted_data_update = dash.no_update
    graph_figure_update = dash.no_update
    download_btn_update = dash.no_update

    # We dispatch different actions based on how this callback was triggered.
    # This is due to a limitation in Dash of components not being able to be
    # the output of more than one callback, meaning that we often have to
    # consolidate behaviour in monolithic callbacks.
    if not ctx.triggered:
        trigger = None
    else:
        trigger = ctx.triggered[0]["prop_id"].split(".")[0]

    # If the callback was triggered by pressing "plot" in the settings
    if trigger == "settings-card-submit":
        # Query for data based on the selected settings
        data, node_id_x, node_id_y = get_data_from_settings(
            x_value, y_value, colour, x_filter, y_filter
        )

        # Filter data
        plotted_data_json, removed_eids = get_filtered_data(
            data, x_value, y_value, x_filter, y_filter
        )
        graph_data_update = data

        # Compute summary statistics
        statistics_update = get_statistics(removed_eids, node_id_x, node_id_y)
        plotted_data_update = plotted_data_json
        graph_figure_update = get_field_plot(
            removed_eids, x_value, y_value, colour, graph_type, trendline
        )
        download_btn_update = False

    # If the callback was triggered by a selection on the plot (i.e. lasso tool)
    elif trigger == "graph" and selected_data:
        points = selected_data["points"]
        points = [(p["x"], p["y"]) for p in points]
        points_x, points_y = zip(*points)
        df = None
        node_id_x = None
        node_id_y = None

        if x_value is not None:
            node_id_x = NodeIdentifier(x_value)
            df = pd.DataFrame({node_id_x.field_id: points_x})
        if y_value is not None:
            node_id_y = NodeIdentifier(y_value)
            df = pd.DataFrame(
                {node_id_x.field_id: points_x, node_id_y.field_id: points_y}
            )

        # Compute summary statistics of the sub-selection
        statistics_update = get_statistics(df, node_id_x, node_id_y)
        data = pd.read_json(current_data, orient="split")
        plotted_data_json = data.loc[
            (data[data.columns[1]].isin(points_x))
            & (data[data.columns[2]].isin(points_y))
        ]
        plotted_data_update = plotted_data_json.to_json(
            date_format="iso", orient="split"
        )

    return (
        statistics_update,
        plotted_data_update,
        graph_figure_update,
        # download_btn_update, <- disabled while we have the UK Biobank
        # dataset as part of the data explorer
        True,
        loading_bar_update,
    )


def get_data_from_settings(x_value, y_value, colour, x_filter, y_filter):
    """
    Query the database abstraction for data based on the selected settings
    and prune the result.

    :param x_value: data field on the X axis
    :param y_value: data field on the Y axis
    :param colour: optional colouring parameter
    :param x_filter: optional range filter on @x_value
    :param y_filter: optional range filter on @y_value
    :return:
    """
    data = None
    node_id_y = None
    node_id_x = None
    # get new data if cached data is outdated

    if x_value == "":
        x_value = None

    if y_value == "":
        y_value = None

    if not x_value:
        data = None
    else:
        node_id_x = NodeIdentifier(x_value)
        colour_id = None if (not colour) else NodeIdentifier(colour)
        columns_of_interest = [node_id_x] if (not colour) else [node_id_x, colour_id]
        if not y_value:
            data = prune_data(
                DatasetGateway.submit(Query.from_identifiers(columns_of_interest))
            )
        else:
            node_id_y = NodeIdentifier(y_value)
            columns_of_interest = (
                [node_id_x, node_id_y]
                if (not colour_id)
                else [node_id_x, node_id_y, colour_id]
            )
            data = prune_data(
                DatasetGateway.submit(Query.from_identifiers(columns_of_interest))
            )
    return data, node_id_x, node_id_y


def get_filtered_data(data, x_value, y_value, x_filter, y_filter):
    """
    Apply range filters to the data.

    :param data: current DataFrame
    :param x_value: data field on the X axis
    :param y_value: data field on the Y axis
    :param x_filter: optional range filter on @x_value
    :param y_filter: optional range filter on @y_value
    :return: filtered DataFrame
    """
    filtered_data = _filter_data_aux(data, x_value, x_filter)
    filtered_data = _filter_data_aux(filtered_data, y_value, y_filter)
    plotted_data_json = filtered_data.to_json(date_format="iso", orient="split")

    removed_eids = filtered_data.loc[:, filtered_data.columns != "eid"]

    return plotted_data_json, removed_eids


def _filter_data_aux(filtered_data, value, filter):
    """Applies a single filter to data"""
    if value != "" and filter is not None:
        node_id = NodeIdentifier(value)
        filtered_data = filtered_data[
            filtered_data[node_id.db_id()].between(filter[0], filter[1])
        ]
    return filtered_data
