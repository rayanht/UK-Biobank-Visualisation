import pandas as pd
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from src.dash_app import dash, app

from src.dataset_gateway import DatasetGateway, Query
from src.graph import (
    filter_data,
    get_field_plot,
    get_statistics,
    prune_data,
)
from src.tree.node import NodeIdentifier

# Functions to get ids of components
from src.setting.instance_setting import get_dropdown_id as get_inst_dropdown_id
from src.setting.filter_setting import get_slider_id

def get_button(var=None):
    return dbc.Button(
                "Plot graph",
                id="settings-card-submit",
                color="primary",
                className="mt-2",
            )

# store x_value, y_value and colour too in the dcc.store,
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
        State(component_id=get_inst_dropdown_id('x'), component_property="value"),
        State(component_id=get_inst_dropdown_id('y'), component_property="value"),
        State(component_id="settings-graph-type-dropdown", component_property="value"),
        # colour
        State(component_id="settings-graph-colour-dropdown", component_property="value"),
        # filters
        State(component_id=get_slider_id('x'), component_property="value"),
        State(component_id=get_slider_id('y'), component_property="value"),
    ],
)
def get_data(n, cached_data, x_value, y_value, graph_type, colour, x_filter, y_filter):
    new_cached_data = dash.no_update
    data = None
    # get new data if cached data is outdated
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
            colour_id = NodeIdentifier(colour) if (colour != None) else None
            columns_of_interest = [node_id_x] if (colour == None) else [node_id_x, colour_id]
            if not y_value:
                data = prune_data(
                    DatasetGateway.submit(Query.from_identifiers(columns_of_interest))
                )
                new_cached_data = {
                    "x-value": x_value,
                    "y-value": "",
                    "colour": colour,
                    "data": data.to_json(date_format="iso", orient="split"),
                }
                print("Getting new data!")
            else:
                node_id_y = NodeIdentifier(y_value)
                columns_of_interest = [node_id_x, node_id_y] \
                                        if (colour_id == None) else \
                                            [node_id_x, node_id_y, colour_id]
                data = prune_data(
                    DatasetGateway.submit(Query.from_identifiers(columns_of_interest))
                )
                new_cached_data = {
                    "x-value": x_value,
                    "y-value": y_value,
                    "colour": colour,
                    "data": data.to_json(date_format="iso", orient="split"),
                }
                print("Getting new data!")
    # if cache data is not outdated, use it
    else:
        print(
            f"Using cached data for {cached_data['x-value']} {cached_data['y-value']} and {cached_data['colour']}, current x is {x_value} y is {y_value} colour is {colour}"
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
        get_field_plot(removed_eids, x_value, y_value, colour, graph_type),
        get_statistics(removed_eids, x_value, y_value),
        False,
    )
