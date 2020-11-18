from os import name
import pandas as pd
from pandas.core.frame import DataFrame
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np
import functools
import plotly.express as px
from plotly.subplots import make_subplots
from enum import Enum
from src.dataset_gateway import field_id_meta_data, data_encoding_meta_data
from src.tree.node import NodeIdentifier
from src.tree.node_utils import get_field_names_to_inst, get_sex_node_identifier


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

def is_categorical_data(node_id: NodeIdentifier):
    node_field_type = get_field_type(node_id.field_id)
    return node_field_type == ValueType.CAT_MULT or node_field_type == ValueType.CAT_SINGLE

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

    def violin_plot(
        self,
        node_id: NodeIdentifier,
        filtered_data: pd.DataFrame,
        colour_id: NodeIdentifier,
    ):
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        encoding_dict = None
        if colour_id:
            # Rename entries of colour column to name of labels
            encoding_dict = rename_category_entries(filtered_data, colour_id)
        for col in filtered_data:
            for trace in self.get_violin_traces(col, filtered_data, colour_id, encoding_dict):
                fig.add_trace(trace)
        fig.update_layout(violinmode="overlay", violingap=0)
        return self.format_graph(fig, node_id, (not colour_id))

    def get_violin_traces(
        self, 
        col: str, 
        filtered_data: pd.DataFrame, 
        colour_id: NodeIdentifier, 
        encoding_dict: dict
    ):
        if colour_id == None:
            trace = go.Violin(
                y=filtered_data[col],
                name=col,
                box_visible=True,
                line_color="black",
                meanline_visible=True,
                opacity=0.6,
            )
            return [trace]
        colour_axes_name = self.get_graph_axes_title(colour_id)
        # TODO: implement logic for categorical colour
        if col != colour_axes_name:
            trace1 = go.Violin(
                y=filtered_data[col][filtered_data[colour_axes_name] == 0],
                legendgroup="Female",
                scalegroup=col,
                name=col,
                side="negative",
                meanline_visible=True,
                box_visible=True,
                line_color="blue",
                fillcolor="blue",
                opacity=0.6,
                showlegend=False,
            )
            trace2 = go.Violin(
                y=filtered_data[col][filtered_data[colour_axes_name] == 1],
                legendgroup="Male",
                scalegroup=col,
                name=col,
                side="positive",
                meanline_visible=True,
                box_visible=True,
                line_color="orange",
                fillcolor="orange",
                opacity=0.6,
                showlegend=False,
            )
            return [trace1, trace2]
        return self.get_empty_sex_traces()

    def get_empty_sex_traces(self):
        trace1 = go.Violin(
            y=[None],
            legendgroup="Female",
            scalegroup="Female",
            name="Female",
            line_color="blue",
            fillcolor="blue",
        )
        trace2 = go.Violin(
            y=[None],
            legendgroup="Male",
            scalegroup="Male",
            name="Male",
            line_color="orange",
            fillcolor="orange",
        )
        return [trace1, trace2]

    def scatter_plot(
        self,
        node_id_x: NodeIdentifier,
        node_id_y: NodeIdentifier,
        filtered_data: pd.DataFrame,
        colour_id: NodeIdentifier,
    ):
        if colour_id != None:
            if is_categorical_data(colour_id):
                # If colour is categorical data, rename entries to name of labels
                rename_category_entries(filtered_data, colour_id)

        colour_name = (
            None if (colour_id == None) else self.get_graph_axes_title(colour_id)
        )
        fig = px.scatter(
            data_frame=filtered_data,
            x=self.get_graph_axes_title(node_id_x),
            y=self.get_graph_axes_title(node_id_y),
            color=colour_name,
        )
        return self.format_graph_two_var(fig, node_id_x, node_id_y, (colour_id != None))

    def bar_plot(
        self,
        node_id: NodeIdentifier,
        filtered_data: pd.DataFrame,
        colour_id: NodeIdentifier,
    ):
        colour_name = (
            None if (colour_id == None) else self.get_graph_axes_title(colour_id)
        )
        processed_df = to_categorical_data(node_id, filtered_data, colour_name)
        fig = px.bar(processed_df, x="categories", y="counts", color=colour_name)
        return self.format_graph(fig, node_id, (colour_id != None))

    def pie_plot(
        self, node_id: NodeIdentifier, filtered_data: pd.DataFrame, colour_id=None
    ):
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


def get_statistics(data, node_id_x: NodeIdentifier, node_id_y: NodeIdentifier = None):
    """Update the summary statistics when the dropdown selection changes"""
    if (node_id_x is None) | (data is None):
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
    stats.insert(0, "Variables", var_names)
    return dbc.Table.from_dataframe(stats, striped=True, bordered=True, hover=True)


def get_field_plot(
    filtered_data: DataFrame, str_id_x, str_id_y, str_id_colour, graph_type
):
    """Returns a graph containing columns of the same field"""
    node_id_x = NodeIdentifier(str_id_x)
    colour_id = NodeIdentifier(str_id_colour) if (str_id_colour != None) else None
    # Drop row that contains column ids
    filtered_data = drop_row_with_col_id(filtered_data, node_id_x)

    if not str_id_y:
        renamed_data = filtered_data.rename(
            columns=get_column_names([node_id_x, colour_id])
        )
        return switcher[graph_type](node_id_x, renamed_data, colour_id)
    node_id_y = NodeIdentifier(str_id_y)
    renamed_data = filtered_data.rename(
        columns=get_column_names([node_id_x, node_id_y, colour_id])
    )
    return switcher[graph_type](node_id_x, node_id_y, renamed_data, colour_id)


def drop_row_with_col_id(data, node_id):
    column_id_rows = data[data[node_id.db_id()] == node_id.meta_id()].index.values
    for row_id in reversed(column_id_rows):
        data = data.drop(row_id)
    return data


def get_column_names(node_ids):
    return {
        node_id.db_id(): graph.get_graph_axes_title(node_id)
        for node_id in node_ids
        if (node_id != None)
    }


@functools.lru_cache
def get_field_type(field_id):
    df = field_id_meta_data()
    x_value_type_id = int(df.loc[df["field_id"] == field_id]["value_type"].values[0])
    return ValueType(x_value_type_id)

def get_categorical_dict(node_id):
    """Returns a dict relating encoding to name of each label in category"""
    field_id_meta = field_id_meta_data()
    encoding_id = int(
        field_id_meta.loc[field_id_meta["field_id"] == str(node_id.field_id)][
            "encoding_id"
        ].values[0]
    )
    return data_encoding_meta_data(encoding_id)

def to_categorical_data(node_id, filtered_data, colour_name=None):
    """Process categorical data and returns the frequency of each label"""
    encoding_dict = get_categorical_dict(node_id)

    # Define columns of interest
    subset = (
        [graph.get_graph_axes_title(node_id)]
        if (colour_name == None)
        else [graph.get_graph_axes_title(node_id), colour_name]
    )
    columns_of_interest = (
        [graph.get_graph_axes_title(node_id), "counts"]
        if (colour_name == None)
        else [graph.get_graph_axes_title(node_id), colour_name, "counts"]
    )
    columns_to_return = (
        ["categories", "counts"]
        if (colour_name == None)
        else [colour_name, "categories", "counts"]
    )

    # Get count of occurrences of data
    encoding_counts = filtered_data.value_counts(
        sort=False, subset=subset
    ).reset_index()
    encoding_counts.columns = columns_of_interest
    encoding_counts["categories"] = (
        encoding_counts[graph.get_graph_axes_title(node_id)]
        .astype(int)
        .map(encoding_dict)
    )

    return encoding_counts[columns_to_return]


def rename_category_entries(filtered_data, node_id):
    """Modify entries of the specific column of input dataframe to label names"""
    encoding_dict = get_categorical_dict(node_id)
    print(encoding_dict)
    column_name = graph.get_graph_axes_title(node_id)
    filtered_data[column_name] = (
        filtered_data[column_name].astype(int).map(encoding_dict)
    )
    return encoding_dict


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
