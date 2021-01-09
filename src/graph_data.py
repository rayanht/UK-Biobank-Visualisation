import math
import time

import pandas as pd
from pandas.core.frame import DataFrame
import dash_bootstrap_components as dbc
import functools
from src.value_type import ValueType
from src.dataset_gateway import field_id_meta_data, data_encoding_meta_data
from src.tree.node import NodeIdentifier
from src.tree.node_utils import get_field_names_to_inst


def largest_triangle_three_buckets(data: pd.DataFrame, ratio=0.5):
    columns = data.columns
    data = list(data.itertuples(index=False, name=None))
    threshold = int(ratio * len(data))
    # Bucket size. Leave room for start and end data points
    every = (len(data) - 2) / (threshold - 2)

    a = 0  # Initially a is the first point in the triangle
    next_a = 0
    max_area_point = (0, 0)

    sampled = [data[0]]  # Always add the first point

    for i in range(0, threshold - 2):
        # Calculate point average for next bucket (containing c)
        avg_x = 0
        avg_y = 0
        avg_range_start = int(math.floor((i + 1) * every) + 1)
        avg_range_end = int(math.floor((i + 2) * every) + 1)
        avg_rang_end = avg_range_end if avg_range_end < len(data) else len(data)

        avg_range_length = avg_rang_end - avg_range_start

        while avg_range_start < avg_rang_end:
            avg_x += data[avg_range_start][0]
            avg_y += data[avg_range_start][1]
            avg_range_start += 1

        avg_x /= avg_range_length
        avg_y /= avg_range_length

        # Get the range for this bucket
        range_offs = int(math.floor((i + 0) * every) + 1)
        range_to = int(math.floor((i + 1) * every) + 1)

        # Point a
        point_ax = data[a][0]
        point_ay = data[a][1]

        max_area = -1

        while range_offs < range_to:
            # Calculate triangle area over three buckets
            area = (
                math.fabs(
                    (point_ax - avg_x) * (data[range_offs][1] - point_ay)
                    - (point_ax - data[range_offs][0]) * (avg_y - point_ay)
                )
                * 0.5
            )

            if area > max_area:
                max_area = area
                max_area_point = data[range_offs]
                next_a = range_offs  # Next a is this b
            range_offs += 1

        sampled.append(max_area_point)  # Pick this point from the bucket
        a = next_a  # This a is the next a (chosen b)

    sampled.append(data[len(data) - 1])  # Always add last

    return pd.DataFrame(sampled, columns=columns)


def is_categorical_data(node_id: NodeIdentifier):
    node_field_type = get_field_type(node_id.field_id)
    return (
        node_field_type == ValueType.CAT_MULT or node_field_type == ValueType.CAT_SINGLE
    )


def has_multiple_instances(field_info):
    return field_info["instanced"].values[0] == 1


@functools.lru_cache
def get_field_type(field_id):
    df = field_id_meta_data()
    x_value_type_id = int(df[df["field_id"] == int(field_id)]["value_type"].values[0])
    return ValueType(x_value_type_id)


def get_categorical_dict(node_id):
    """Returns a dict relating encoding to name of each label in category"""
    field_id_meta = field_id_meta_data()
    encoding_id = int(
        field_id_meta.loc[field_id_meta["field_id"] == int(node_id.field_id)][
            "encoding_id"
        ].values[0]
    )
    return data_encoding_meta_data(encoding_id)


def filter_data(dataframe: DataFrame, x_value, y_value, x_filter, y_filter):
    filtered_data = _filter_data_aux(dataframe, x_value, x_filter)
    filtered_data = _filter_data_aux(filtered_data, y_value, y_filter)
    return filtered_data


def _filter_data_aux(filtered_data, value, filter):
    """Applies a single filter to data"""
    if value != "" and filter is not None:
        print(filtered_data)
        node_id = NodeIdentifier(value)
        filtered_data = filtered_data[
            filtered_data[node_id.db_id()].between(filter[0], filter[1])
        ]
    return filtered_data


def prune_data(dataframe: DataFrame):
    prune_data = dataframe.replace("", float("NaN"))
    data_columns = prune_data.columns
    for column in data_columns:
        prune_data[column] = pd.to_numeric(prune_data[column], errors="coerce")
    remove_non_numeric = prune_data.dropna(how="any")
    return remove_non_numeric


# Global data used for all operations
field_names_to_inst = get_field_names_to_inst()
field_names_to_ids = field_names_to_inst.loc[
    field_names_to_inst["InstanceID"].isnull()
][["FieldID", "NodeName"]].dropna(how="any", axis=0)
field_names_to_ids["FieldID"] = field_names_to_ids["FieldID"].apply(
    lambda field_id: str(int(field_id))
)
pd.set_option("display.max_rows", None, "display.max_columns", None)


def get_field_name(field_id):
    row_with_name = field_names_to_ids.loc[
        field_names_to_ids["FieldID"] == str(field_id), "NodeName"
    ]
    return row_with_name.item()


def get_graph_axes_title(node_id: NodeIdentifier):
    if not node_id:
        return None
    return f"{get_field_name(node_id.field_id)} ({node_id.db_id()})"


def get_inst_name_dict(field_id):
    field_id_meta = field_id_meta_data()
    field_info = field_id_meta[field_id_meta["field_id"] == int(field_id)]
    inst_names = field_names_to_inst.loc[
        field_names_to_inst["FieldID"] == int(field_id)
    ].copy()

    if has_multiple_instances(field_info):
        # There are multiple instances. Drop row with field name
        inst_names = inst_names.loc[inst_names["InstanceID"].notnull()]
        inst_names["MetaID"] = inst_names.apply(
            (lambda row: f"{field_id}-{int(row.InstanceID)}.0"), axis=1
        )
    else:
        instance = (
            field_info["instance_min"].iloc[0]
            if inst_names["InstanceID"].isna().values.any()
            else inst_names["InstanceID"].iloc[0]
        )
        inst_names["MetaID"] = field_id + f"-{instance}.0"
    inst_name_dict = dict(zip(inst_names["MetaID"], inst_names["NodeName"]))
    return inst_name_dict


def to_categorical_data(node_id, filtered_data, colour_name=None):
    """Process categorical data and returns the frequency of each label"""
    encoding_dict = get_categorical_dict(node_id)

    # Define columns of interest
    subset = (
        [get_graph_axes_title(node_id)]
        if (colour_name == None)
        else [get_graph_axes_title(node_id), colour_name]
    )
    columns_of_interest = (
        [get_graph_axes_title(node_id), "counts"]
        if (colour_name == None)
        else [get_graph_axes_title(node_id), colour_name, "counts"]
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
        encoding_counts[get_graph_axes_title(node_id)].astype(int).map(encoding_dict)
    )

    return encoding_counts[columns_to_return]


def rename_category_entries(filtered_data, node_id):
    """Modify entries of the specific column of input dataframe to label names"""
    encoding_dict = get_categorical_dict(node_id)
    column_name = get_graph_axes_title(node_id)
    filtered_data[column_name] = (
        filtered_data[column_name].astype(int).map(encoding_dict)
    )
    return encoding_dict


def get_inst_names_options(raw_id):
    "Returns a dict of options for a dropdown list of instances"
    field_id = NodeIdentifier(raw_id).field_id
    return get_inst_name_dict(field_id)


def get_statistics(data, node_id_x: NodeIdentifier, node_id_y: NodeIdentifier = None):
    """Update the summary statistics when the dropdown selection changes"""
    if (node_id_x is None) | (data is None):
        return "No data to display"

    data_x = data.iloc[:, 0]
    stats_x = data_x.describe()
    stats = pd.DataFrame(stats_x)
    var_names = [get_field_name(node_id_x.field_id)]
    if not (node_id_y is None):
        stats_y = data.iloc[:, 1].describe()
        stats = pd.concat([stats_x, stats_y], axis=1)
        var_names.append(get_field_name(node_id_y.field_id))
    stats = stats.transpose()
    stats.insert(0, "Variables", var_names)
    return dbc.Table.from_dataframe(stats, striped=True, bordered=True, hover=True)


def get_column_names(node_ids):
    return {
        node_id.db_id(): get_graph_axes_title(node_id)
        for node_id in node_ids
        if (node_id != None)
    }
