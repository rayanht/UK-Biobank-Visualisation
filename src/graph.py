import pandas as pd
from pandas.core.frame import DataFrame
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
from enum import Enum
from src.dataset_gateway import (
    DatasetGateway,
    Query,
    field_id_meta_data,
    data_encoding_meta_data,
)
from src.tree.node import NodeIdentifier
from src.tree.node_utils import get_field_names_to_inst


def has_multiple_instances(meta_ids):
    for i in range(len(meta_ids) - 1):
        diff_inst = (
            NodeIdentifier(meta_ids[i]).instance_id
            != NodeIdentifier(meta_ids[i + 1]).instance_id
        )
        if diff_inst:
            return True
    return False


def has_array_items(meta_ids):
    if len(meta_ids) <= 1:
        return False
    return NodeIdentifier(meta_ids[0]).part_id != NodeIdentifier(meta_ids[1]).part_id


class Graph:
    def __init__(self):
        self.field_names_to_inst = get_field_names_to_inst()
        self.field_names_to_ids = self.field_names_to_inst.loc[
            self.field_names_to_inst["InstanceID"].isnull()
        ][["FieldID", "NodeName"]].dropna(how="any", axis=0)
        self.field_names_to_ids["FieldID"] = self.field_names_to_ids["FieldID"].apply(
            lambda field_id: str(int(field_id))
        )
        pd.set_option("display.max_rows", None, "display.max_columns", None)

    def get_field_name(self, field_id):
        return self.field_names_to_ids.loc[
            self.field_names_to_ids["FieldID"] == field_id, "NodeName"
        ].item()

    def get_graph_axes_title(self, node_id: NodeIdentifier):
        return f"{self.get_field_name(node_id.field_id)} ({node_id.db_id()})"

    def get_inst_name_dict(self, field_id):
        inst_names = self.field_names_to_inst.loc[
            self.field_names_to_inst["FieldID"] == int(field_id)
        ].copy()
        if len(inst_names) > 1:
            # There are multiple instances. Drop row with field name
            inst_names = inst_names.loc[inst_names["InstanceID"].notnull()]
            inst_names["MetaID"] = inst_names.apply(
                lambda row: f"{field_id}-{int(row.InstanceID)}.0", axis=1
            )
        else:
            inst_names["MetaID"] = field_id + "-0.0"
        inst_name_dict = dict(zip(inst_names["MetaID"], inst_names["NodeName"]))
        return inst_name_dict

    def violin_plot(self, node_id: NodeIdentifier, filtered_data: pd.DataFrame):
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        for col in filtered_data:
            trace = go.Violin(
                y=filtered_data[col],
                name=col,
                box_visible=True,
                line_color="black",
                meanline_visible=True,
                fillcolor="lightseagreen",
                opacity=0.6,
            )
            fig.add_trace(trace)
        return self.format_graph(fig, node_id, False)

    def scatter_plot(
        self,
        node_id_x: NodeIdentifier,
        node_id_y: NodeIdentifier,
        filtered_data: pd.DataFrame,
    ):
        fig = px.scatter(
            data_frame=filtered_data,
            x=self.get_graph_axes_title(node_id_x),
            y=self.get_graph_axes_title(node_id_y),
        )
        return self.format_graph_two_var(fig, node_id_x, node_id_y, False)

    def bar_plot(self, node_id: NodeIdentifier, filtered_data: pd.DataFrame):
        processed_df = to_categorical_data(node_id, filtered_data)
        fig = px.bar(processed_df, x="categories", y="counts")
        return self.format_graph(fig, node_id, False)

    def pie_plot(self, node_id: NodeIdentifier, filtered_data: pd.DataFrame):
        processed_df = to_categorical_data(node_id, filtered_data)
        fig = px.pie(processed_df, names="categories", values="counts")
        return self.format_graph(fig, node_id, True)

    def format_graph(self, fig, node_id, showlegend):
        fig.update_layout(
            title={
                "text": self.get_field_name(node_id.field_id),
                "y": 0.95,
                "x": 0.475,
                "xanchor": "center",
                "yanchor": "top",
            },
            showlegend=showlegend,
        )
        return fig

    def format_graph_two_var(self, fig, node_id_x, node_id_y, showlegend):
        fig.update_layout(
            title={
                "text": f"{self.get_field_name(node_id_y.field_id)} against {self.get_field_name(node_id_x.field_id)}",
                "y": 0.95,
                "x": 0.475,
                "xanchor": "center",
                "yanchor": "top",
            },
            showlegend=showlegend,
        )
        return fig


graph = Graph()
switcher = {
    1: graph.violin_plot,
    2: graph.scatter_plot,
    3: graph.bar_plot,
    4: graph.pie_plot,
}


def prune_data(dataframe: DataFrame):
    prune_data = dataframe.replace("", float("NaN"))
    data_columns = prune_data.columns
    for column in data_columns:
        prune_data[column] = pd.to_numeric(prune_data[column], errors="coerce")
    remove_non_numeric = prune_data.dropna(how="any")
    return remove_non_numeric


def filter_data(dataframe: DataFrame, x_value, y_value, x_filter, y_filter):
    # filter by x_value
    filtered_data = dataframe
    if x_value != "" and x_filter is not None:
        node_id_x = NodeIdentifier(x_value)
        filtered_data = filtered_data[
            filtered_data[node_id_x.db_id()].between(x_filter[0], x_filter[1])
        ]
    if y_value != "" and y_filter is not None:
        node_id_y = NodeIdentifier(y_value)
        filtered_data = filtered_data[
            filtered_data[node_id_y.db_id()].between(y_filter[0], y_filter[1])
        ]
    return filtered_data


def get_statistics(data, x_value, node_id_x : NodeIdentifier, y_value=None, node_id_y : NodeIdentifier = None):
    """Update the summary statistics when the dropdown selection changes"""
    if (x_value is None) | (data is None):
        return "No data to display"

    data_x = data.iloc[:, 0]
    stats_x = data_x.describe()
    stats = pd.DataFrame(stats_x)
    var_names = [graph.get_field_name(node_id_x.field_id)]
    if not (node_id_y is None):
        stats_y = data.iloc[:, 1].describe()
        stats = pd.concat([stats_x, stats_y], axis=1)
        var_names.append(graph.get_field_name(node_id_y.field_id))
    stats = stats.transpose()
    stats.insert(0, 'Variables', var_names)
    return dbc.Table.from_dataframe(
        stats, striped=True, bordered=True, hover=True
    )


def get_field_plot(filtered_data: DataFrame, str_id_x, str_id_y, graph_type):
    """Returns a graph containing columns of the same field"""
    node_id_x = NodeIdentifier(str_id_x)
    if not str_id_y:
        renamed_data = filtered_data.rename(
            columns={node_id_x.db_id(): graph.get_graph_axes_title(node_id_x)}
        )
        return switcher[graph_type](node_id_x, renamed_data)
    node_id_y = NodeIdentifier(str_id_y)
    renamed_data = filtered_data.rename(
        columns={
            node_id_x.db_id(): graph.get_graph_axes_title(node_id_x),
            node_id_y.db_id(): graph.get_graph_axes_title(node_id_y),
        }
    )
    return switcher[graph_type](node_id_x, node_id_y, renamed_data)


def to_categorical_data(node_id, filtered_data):
    # Convert categorical data into a bar plot
    field_id_meta = field_id_meta_data()
    encoding_id = int(
        field_id_meta.loc[field_id_meta["field_id"] == str(node_id.field_id)][
            "encoding_id"
        ].values[0]
    )
    encoding_dict = data_encoding_meta_data(encoding_id)

    # Get column of interest, dropping first row which contains node_id
    column_of_interest = filtered_data[graph.get_graph_axes_title(node_id)]

    encoding_counts = (
        column_of_interest.value_counts(dropna=True)
        .rename_axis("unique_values")
        .reset_index(name="counts")
    )
    encoding_counts["categories"] = encoding_counts["unique_values"].map(encoding_dict)

    return encoding_counts[["categories", "counts"]]


# returns a dict of options for a dropdown list of instances
def get_inst_names_options(raw_id):
    field_id = NodeIdentifier(raw_id).field_id
    return graph.get_inst_name_dict(field_id)


class ValueType(Enum):
    INTEGER = (11, "Integer", [1])
    CAT_SINGLE = (21, "Categorical (single)", [3, 4])
    CAT_MULT = (22, "Categorical (multiple)", [3, 4])
    CONT = (31, "Continuous", [1])
    TEXT = (41, "Text", [])
    DATE = (51, "Date", [])
    TIME = (61, "Time", [])
    COMPOUND = (101, "Compound", [])

    def __init__(self, type_id, label, supported_graphs):
        self.type_id = type_id
        self.label = label
        self.supported_graphs = supported_graphs

    def __new__(cls, *values):
        obj = object.__new__(cls)
        # first value is canonical value
        obj._value_ = values[0]
        obj._all_values = values
        return obj

    def __repr__(self):
        return "<%s.%s: %s>" % (
            self.__class__.__name__,
            self._name_,
            ", ".join([repr(v) for v in self._all_values]),
        )
