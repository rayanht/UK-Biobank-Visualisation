import inspect

import pandas as pd
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from src.dash_app import dash, app

from src.dataset_gateway import DatasetGateway, Query
from src.graph import filter_data, get_field_plot, get_statistics, prune_data
from src.tree.node import NodeIdentifier

# Functions to get ids of components
from src.setting.instance_setting import get_dropdown_id as get_inst_dropdown_id
from src.setting.colour_setting import get_dropdown_id as get_colour_dropdown_id
from src.setting.filter_setting import get_slider_id


def get_button(var=None):
    return dbc.Button(
        "Plot graph", id="settings-card-submit", color="primary", className="mt-2"
    )


# store x_value, y_value and colour too in the dcc.store,
# if not the same as current selected ones, then no_update. it will be called again once the store is updated with new and correct data
# if the same, then update using the settings
# this makes it faster for changing settings without having to query database again
@app.callback(
    [
        Output(component_id="graph-data", component_property="data"),
        Output(component_id="statistics", component_property="children"),
        Output(component_id="plotted-data", component_property="data"),
        Output(component_id="graph", component_property="figure"),
        Output(component_id="download-btn", component_property="disabled"),
    ],
    [
        Input(component_id="graph", component_property="selectedData"),
        Input(component_id="settings-card-submit", component_property="n_clicks"),
    ],
    [
        State(component_id="graph-data", component_property="data"),
        State(component_id=get_inst_dropdown_id("x"), component_property="value"),
        State(component_id=get_inst_dropdown_id("y"), component_property="value"),
        State(component_id="settings-graph-type-dropdown", component_property="value"),
        # colour
        State(component_id=get_colour_dropdown_id(), component_property="value"),
        # filters
        State(component_id=get_slider_id("x"), component_property="value"),
        State(component_id=get_slider_id("y"), component_property="value"),
    ],
)
def get_data(
    selected_data,
    n,
    cached_data,
    x_value,
    y_value,
    graph_type,
    colour,
    x_filter,
    y_filter,
):

    ctx = dash.callback_context

    graph_data_update = dash.no_update
    statistics_update = dash.no_update
    plotted_data_update = dash.no_update
    graph_figure_update = dash.no_update
    download_btn_update = dash.no_update

    if not ctx.triggered:
        trigger = None
    else:
        trigger = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger == "settings-card-submit":

        data, new_cached_data, node_id_x, node_id_y = get_data_from_settings(
            cached_data, x_value, y_value, colour, x_filter, y_filter
        )

        if data is None:
            graph_data_update = new_cached_data
            statistics_update = "No data to display"
            plotted_data_update = None
            graph_figure_update = {
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
            download_btn_update = True

        else:
            # filter data
            plotted_data_json, removed_eids = get_filtered_data(
                data, x_value, y_value, x_filter, y_filter
            )
            graph_data_update = new_cached_data
            statistics_update = get_statistics(removed_eids, node_id_x, node_id_y)
            plotted_data_update = plotted_data_json
            graph_figure_update = get_field_plot(
                removed_eids, x_value, y_value, colour, graph_type
            )
            download_btn_update = False

    elif trigger == "graph" and selected_data:
        points = selected_data["points"]
        points = [(p["x"], p["y"]) for p in points]
        points_x, points_y = zip(*points)
        df = None
        node_id_x = None
        node_id_y = None

        if x_value is not None:
            node_id_x = NodeIdentifier(x_value)
            df = pd.DataFrame({"x": points_x})
        if y_value is not None:
            node_id_y = NodeIdentifier(y_value)
            df = pd.DataFrame({"x": points_x, "y": points_y})

        statistics_update = get_statistics(df, node_id_x, node_id_y)

    return (
        graph_data_update,
        statistics_update,
        plotted_data_update,
        graph_figure_update,
        download_btn_update,
    )


def get_data_from_settings(cached_data, x_value, y_value, colour, x_filter, y_filter):
    new_cached_data = dash.no_update
    data = None
    node_id_y = None
    node_id_x = None
    # get new data if cached data is outdated

    if x_value == "":
        x_value = None

    if y_value == "":
        y_value = None

    if (
        not cached_data
        or cached_data["x-value"] != x_value
        or cached_data["y-value"] != y_value
        or cached_data["colour"] != colour
    ):
        if not x_value:
            new_cached_data = None
            data = None
        else:
            node_id_x = NodeIdentifier(x_value)
            colour_id = NodeIdentifier(colour) if (colour is not None) else None
            columns_of_interest = (
                [node_id_x] if (colour is None) else [node_id_x, colour_id]
            )
            if not y_value:
                data = prune_data(
                    DatasetGateway.submit(Query.from_identifiers(columns_of_interest))
                )
                new_cached_data = {
                    "x-value": x_value,
                    "y-value": None,
                    "colour": colour,
                    "data": data.to_json(date_format="iso", orient="split"),
                }
                if cached_data:
                    print(
                        f"{ cached_data['x-value'] } != {x_value}, { cached_data['y-value'] } != {y_value}, { cached_data['colour'] } != {colour}. Getting new data!"
                    )
                else:
                    print(f"Cached data is none. Getting new data!")
            else:
                node_id_y = NodeIdentifier(y_value)
                columns_of_interest = (
                    [node_id_x, node_id_y]
                    if (colour_id is None)
                    else [node_id_x, node_id_y, colour_id]
                )
                data = prune_data(
                    DatasetGateway.submit(Query.from_identifiers(columns_of_interest))
                )
                new_cached_data = {
                    "x-value": x_value,
                    "y-value": y_value,
                    "colour": colour,
                    "data": data.to_json(date_format="iso", orient="split"),
                }
                if cached_data:
                    print(
                        f"{ cached_data['x-value'] } != {x_value}, { cached_data['y-value'] } != {y_value}, { cached_data['colour'] } != {colour}. Getting new data!"
                    )
                else:
                    print(f"Cached data is none. Getting new data!")
    # if cache data is not outdated, use it
    else:
        print(inspect.stack()[1].function)
        print(
            f"Using cached data for {cached_data['x-value']} {cached_data['y-value']} and {cached_data['colour']}, current x is {x_value} y is {y_value} colour is {colour}"
        )
        data = pd.read_json(cached_data["data"], orient="split")
        if x_value:
            node_id_x = NodeIdentifier(x_value)
        if y_value:
            node_id_y = NodeIdentifier(y_value)

    return data, new_cached_data, node_id_x, node_id_y


def get_filtered_data(data, x_value, y_value, x_filter, y_filter):
    filtered_data = filter_data(data, x_value, y_value, x_filter, y_filter)
    plotted_data_json = filtered_data.to_json(date_format="iso", orient="split")

    removed_eids = filtered_data.loc[:, filtered_data.columns != "eid"]

    return plotted_data_json, removed_eids
