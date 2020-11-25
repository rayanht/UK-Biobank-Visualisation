import pandas as pd
from pandas.core.frame import DataFrame
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from src.tree.node import NodeIdentifier
from src.graph_data import get_categorical_dict, is_categorical_data,\
    rename_category_entries, to_categorical_data, get_column_names,\
        get_graph_axes_title, get_field_name


class Graph:
    def __init__(self):
        """Nothing to do"""

    def violin_plot(
        self,
        node_id_x: NodeIdentifier,
        node_id_y: NodeIdentifier,
        filtered_data: pd.DataFrame,
        colour_id: NodeIdentifier,
        trendline: int,
    ):
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        colour_encoding_dict = None
        x_encoding_dict = None
        colour_axes_name = None
        x_axes_name = None

        y_columns = filtered_data.columns.values.tolist()

        if colour_id:
            colour_encoding_dict = get_categorical_dict(colour_id)
            colour_axes_name = get_graph_axes_title(colour_id)
            y_columns.remove(colour_axes_name)
        if node_id_y:
            x_encoding_dict = get_categorical_dict(node_id_x)
            x_axes_name = get_graph_axes_title(node_id_x)
            y_columns.remove(x_axes_name)

        for col in y_columns:
            for trace in self.get_violin_traces(
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
        return self.format_graph(fig, node_id_x, (colour_id is not None))

    def get_violin_traces(
        self,
        col: str,
        filtered_data: pd.DataFrame,
        colour_axes_name: str,
        x_axes_name: str,
        x_encoding_dict: dict,
        colour_encoding_dict: dict,
    ):
        if colour_axes_name == None and x_axes_name == None:
            trace = go.Violin(y=filtered_data[col], name=col, line_color="black")
            return [trace]
        traces = []
        if x_axes_name:
            if colour_axes_name:
                for label in colour_encoding_dict:
                    trace = go.Violin(
                        x=filtered_data[x_axes_name][
                            (filtered_data[colour_axes_name] == label)
                        ].replace(x_encoding_dict),
                        y=filtered_data[col][filtered_data[colour_axes_name] == label],
                        name=colour_encoding_dict[label],
                        legendgroup=colour_encoding_dict[label],
                        scalegroup=colour_encoding_dict[label],
                    )
                    traces.append(trace)
            else:
                trace = go.Violin(
                    x=filtered_data[x_axes_name].replace(x_encoding_dict),
                    y=filtered_data[col],
                )
                traces.append(trace)
        else:
            for label in colour_encoding_dict:
                trace = go.Violin(
                    x=filtered_data[colour_axes_name][
                        filtered_data[colour_axes_name] == label
                    ].replace(colour_encoding_dict),
                    y=filtered_data[col][filtered_data[colour_axes_name] == label],
                    name=colour_encoding_dict[label],
                )
                traces.append(trace)
        return traces

    def scatter_plot(
        self,
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

        colour_name = (
            None if (colour_id == None) else get_graph_axes_title(colour_id)
        )

        # Linear trendline
        if trendline == 1:
            fig = px.scatter(
                data_frame=filtered_data,
                x=get_graph_axes_title(node_id_x),
                y=get_graph_axes_title(node_id_y),
                color=colour_name,
                trendline='ols',
                trendline_color_override='red'
            )
        # Non-linear trendline
        elif trendline == 2:
            fig = px.scatter(
                data_frame=filtered_data,
                x=get_graph_axes_title(node_id_x),
                y=get_graph_axes_title(node_id_y),
                color=colour_name,
                trendline='lowess',
                trendline_color_override='red'
            )
        # No trendline
        else:
            fig = px.scatter(
                data_frame=filtered_data,
                x=get_graph_axes_title(node_id_x),
                y=get_graph_axes_title(node_id_y),
                color=colour_name,
            )

        return self.format_graph_two_var(fig, node_id_x, node_id_y, (colour_id != None))

    def bar_plot(
        self,
        node_id_x: NodeIdentifier,
        node_id_y: NodeIdentifier,
        filtered_data: pd.DataFrame,
        colour_id: NodeIdentifier,
        trendline: int,
    ):
        colour_name = (
            None if (colour_id == None) else get_graph_axes_title(colour_id)
        )
        processed_df = to_categorical_data(node_id_x, filtered_data, colour_name)
        fig = px.bar(processed_df, x="categories", y="counts", color=colour_name)
        return self.format_graph(fig, node_id_x, (colour_id != None))

    def pie_plot(
        self,
        node_id_x: NodeIdentifier,
        node_id_y: NodeIdentifier,
        filtered_data: pd.DataFrame,
        colour_id=None,
        trendline=None,
    ):
        processed_df = to_categorical_data(node_id_x, filtered_data)
        fig = px.pie(processed_df, names="categories", values="counts")
        return self.format_graph(fig, node_id_x, True)

    def format_graph(self, fig, node_id, showlegend):
        fig.update_layout(
            title={
                "text": get_field_name(node_id.field_id),
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
                "text": f"{get_field_name(node_id_y.field_id)} against {get_field_name(node_id_x.field_id)}",
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
    return switcher[graph_type](node_id_x, node_id_y, renamed_data, colour_id, trendline)
