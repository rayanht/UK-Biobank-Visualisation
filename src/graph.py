import pandas as pd
from pandas.core.frame import DataFrame
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from src.tree.node import NodeIdentifier
from src.graph_data import (
    get_categorical_dict,
    is_categorical_data,
    rename_category_entries,
    to_categorical_data,
    get_column_names,
    get_graph_axes_title,
    get_field_name,
    largest_triangle_three_buckets,
)


def violin_plot(
    node_id_x: NodeIdentifier,
    node_id_y: NodeIdentifier,
    filtered_data: pd.DataFrame,
    colour_id: NodeIdentifier,
    trendline: int,
):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    y_columns = filtered_data.columns.values.tolist()
    colour_encoding_dict, colour_axes_name = _get_dict_and_title(colour_id, y_columns)
    x_encoding_dict, x_axes_name = _get_dict_and_title(
        node_id_x, y_columns, not node_id_y
    )

    for col in y_columns:
        for trace in _get_violin_traces(
            col,
            filtered_data,
            colour_axes_name,
            x_axes_name,
            x_encoding_dict,
            colour_encoding_dict,
        ):
            fig.add_trace(trace)
    fig.update_traces(meanline_visible=True, box_visible=True, opacity=0.6)
    if node_id_y:
        fig.update_layout(violinmode="group")
    return format_graph(fig, node_id_x, node_id_y, (colour_id is not None))


def _get_dict_and_title(node_id: NodeIdentifier, y_columns, not_cat=False):
    if (not node_id) or not_cat:
        return None, None
    colour_axes_name = get_graph_axes_title(node_id)
    if colour_axes_name in y_columns:
        y_columns.remove(colour_axes_name)
    return get_categorical_dict(node_id), colour_axes_name


def _get_violin_traces(
    col: str,
    filtered_data: pd.DataFrame,
    colour_axes_name: str,
    x_axes_name: str,
    x_encoding_dict: dict,
    colour_encoding_dict: dict,
):
    traces = []
    if (not colour_axes_name) and (not x_axes_name):
        traces.append(go.Violin(y=filtered_data[col], name=col, line_color="black"))
    elif x_axes_name:
        if colour_axes_name:
            for label in colour_encoding_dict:
                traces.append(
                    go.Violin(
                        x=filtered_data[x_axes_name][
                            (filtered_data[colour_axes_name] == label)
                        ].replace(x_encoding_dict),
                        y=filtered_data[col][filtered_data[colour_axes_name] == label],
                        name=colour_encoding_dict[label],
                        legendgroup=colour_encoding_dict[label],
                        scalegroup=colour_encoding_dict[label],
                    )
                )
        else:
            traces.append(
                go.Violin(
                    x=filtered_data[x_axes_name].replace(x_encoding_dict),
                    y=filtered_data[col],
                )
            )
    else:
        for label in colour_encoding_dict:
            traces.append(
                go.Violin(
                    x=filtered_data[colour_axes_name][
                        filtered_data[colour_axes_name] == label
                    ].replace(colour_encoding_dict),
                    y=filtered_data[col][filtered_data[colour_axes_name] == label],
                    name=colour_encoding_dict[label],
                )
            )
    return traces


def scatter_plot(
    node_id_x: NodeIdentifier,
    node_id_y: NodeIdentifier,
    filtered_data: pd.DataFrame,
    colour_id: NodeIdentifier,
    trendline: int,
):
    if colour_id:
        if is_categorical_data(colour_id):
            # If colour is categorical data, rename entries to name of labels
            rename_category_entries(filtered_data, colour_id)
    colour_name = None if (not colour_id) else get_graph_axes_title(colour_id)

    trendline_arg = None
    # Linear trendline
    if trendline == 1:
        trendline_arg = "ols"
    # Non-linear trendline
    elif trendline == 2:
        trendline_arg = "lowess"
    trendline_colour = "red" if trendline_arg else None

    filtered_data = filtered_data.sample(frac=1)
    filtered_data = largest_triangle_three_buckets(filtered_data, 0.25)
    fig = px.scatter(
        data_frame=filtered_data,
        x=get_graph_axes_title(node_id_x),
        y=get_graph_axes_title(node_id_y),
        color=colour_name,
        trendline=trendline_arg,
        trendline_color_override=trendline_colour,
        render_mode="webgl",
    )

    return format_graph(fig, node_id_x, node_id_y, (colour_id is not None))


def bar_plot(
    node_id_x: NodeIdentifier,
    node_id_y: NodeIdentifier,
    filtered_data: pd.DataFrame,
    colour_id: NodeIdentifier,
    trendline: int,
):
    colour_name = None if (colour_id is None) else get_graph_axes_title(colour_id)
    processed_df = to_categorical_data(node_id_x, filtered_data, colour_name)
    fig = px.bar(processed_df, x="categories", y="counts", color=colour_name)
    return format_graph(fig, node_id_x, None, (colour_id is not None))


def pie_plot(
    node_id_x: NodeIdentifier,
    node_id_y: NodeIdentifier,
    filtered_data: pd.DataFrame,
    colour_id=None,
    trendline=None,
):
    processed_df = to_categorical_data(node_id_x, filtered_data)
    fig = px.pie(processed_df, names="categories", values="counts")
    return format_graph(fig, node_id_x, None, True)


def format_graph(fig, node_id_x, node_id_y, showlegend):
    text = (
        f"{get_field_name(node_id_y.field_id)} against {get_field_name(node_id_x.field_id)}"
        if (node_id_y)
        else get_field_name(node_id_x.field_id)
    )
    fig.update_layout(
        title={
            "text": text,
            "y": 0.95,
            "x": 0.475,
            "xanchor": "center",
            "yanchor": "top",
        },
        showlegend=showlegend,
    )
    return fig


switcher = {1: violin_plot, 2: scatter_plot, 3: bar_plot, 4: pie_plot}


def get_field_plot(
    filtered_data: DataFrame, str_id_x, str_id_y, str_id_colour, graph_type, trendline
):
    """Returns a graph containing columns of the same field"""
    node_id_x = NodeIdentifier(str_id_x)
    colour_id = NodeIdentifier(str_id_colour) if (str_id_colour) else None

    if not str_id_y:
        renamed_data = filtered_data.rename(
            columns=get_column_names([node_id_x, colour_id])
        )
        return switcher[graph_type](node_id_x, None, renamed_data, colour_id, trendline)
    node_id_y = NodeIdentifier(str_id_y)
    renamed_data = filtered_data.rename(
        columns=get_column_names([node_id_x, node_id_y, colour_id])
    )
    return switcher[graph_type](
        node_id_x, node_id_y, renamed_data, colour_id, trendline
    )
