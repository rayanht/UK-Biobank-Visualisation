import pandas as pd
import plotly.graph_objects as go
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

    def violin_plot(
        self, 
        node_id: NodeIdentifier, 
        filtered_data: pd.DataFrame, 
        colour_name: str
    ):
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        for col in filtered_data:
            if (col != colour_name):
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
        colour_name: str
    ):
        fig = px.scatter(
            data_frame=filtered_data,
            x=self.get_graph_axes_title(node_id_x),
            y=self.get_graph_axes_title(node_id_y),
        )
        return self.format_graph_two_var(fig, node_id_x, node_id_y, False)

    def bar_plot(
        self, 
        node_id: NodeIdentifier, 
        filtered_data: pd.DataFrame, 
        colour_name: str
    ):
        #TODO: don't drop colour after it is supported in count_values
        if (colour_name != None):
            filtered_data.drop(colour_name, axis='columns', inplace=True)
        processed_df = to_categorical_data(node_id, filtered_data)
        fig = px.bar(processed_df, x="categories", y="counts")
        return self.format_graph(fig, node_id, False)

    def pie_plot(
        self, 
        node_id: NodeIdentifier, 
        filtered_data: pd.DataFrame, 
        colour_name: str
    ):
        #TODO: don't drop colour after it is supported in count_values
        if (colour_name != None):
            filtered_data.drop(colour_name, axis='columns', inplace=True)
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


def get_field_plot(raw_id, graph_type, colour):
    """Returns a graph containing columns of the same field"""
    node_id = NodeIdentifier(raw_id)
    colour_id = NodeIdentifier(colour) if (colour != None) else None
    colour_name = graph.get_graph_axes_title(colour_id) if (colour_id != None) else None
    filtered_data = DatasetGateway.submit(
            Query.from_identifiers([node_id, colour_id])
        ).rename(
        columns=get_column_names([node_id, colour_id])
    )

    fig = switcher[graph_type](node_id, filtered_data, colour_name)
    return fig


def get_two_field_plot(raw_id_x, raw_id_y, graph_type, colour):
    """Returns a graph with two variables"""
    node_id_x = NodeIdentifier(raw_id_x)
    node_id_y = NodeIdentifier(raw_id_y)
    colour_id = NodeIdentifier(colour)
    colour_name = graph.get_graph_axes_title(colour_id)
    filtered_data_x = DatasetGateway.submit(
        Query.from_identifiers([node_id_x, node_id_y, colour_id])
    ).rename(
        columns=get_column_names([node_id_x, node_id_y, colour_id])
    )

    fig = switcher[graph_type](node_id_x, node_id_y, filtered_data_x, colour_name)
    return fig

def get_column_names(node_ids):
    return {node_id.db_id() : graph.get_graph_axes_title(node_id) 
            for node_id in node_ids if (node_id != None)}

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
    column_of_interest = filtered_data[graph.get_graph_axes_title(node_id)].drop(0)

    encoding_counts = column_of_interest.value_counts(dropna=True).rename_axis('unique_values').reset_index(name='counts')
    encoding_counts['categories'] = encoding_counts['unique_values'].astype(int).map(encoding_dict)

    return encoding_counts[["categories", "counts"]]


# returns a dict of options for a dropdown list of instances
def get_inst_names_options(raw_id, isMetaId=True):
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
