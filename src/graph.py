import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.dataset_gateway import DatasetGateway, Query
from src.tree.node import NodeIdentifier
from src.tree.node_utils import get_field_names_to_inst


def has_array_items(meta_ids):
    if len(meta_ids) <= 1:
        return False
    return NodeIdentifier(meta_ids[0]).part_id != NodeIdentifier(meta_ids[1]).part_id


class Graph:

    def __init__(self):
        self.field_names_to_inst = get_field_names_to_inst()
        self.field_names_to_ids \
            = self.field_names_to_inst.loc[self.field_names_to_inst['InstanceID'].isnull()] \
            [['FieldID', 'NodeName']].dropna(how='any', axis=0)
        self.field_names_to_ids['FieldID'] = self.field_names_to_ids['FieldID'].apply(lambda field_id: str(int(field_id)))

    def get_field_name(self, field_id):
        return self.field_names_to_ids.loc[self.field_names_to_ids['FieldID'] == field_id, 'NodeName'].item()

    def get_field_instance_map(self, has_array):
        def get_field_instance_name(meta_id):
            meta_id = NodeIdentifier(meta_id)
            field_id = meta_id.field_id
            inst_id = meta_id.instance_id
            df_with_name = self.field_names_to_inst.loc[(self.field_names_to_inst['FieldID'] == field_id)
                                                        & (self.field_names_to_inst['InstanceID'] == inst_id)][
                'NodeName']
            if has_array:
                part_id = meta_id.part_id
                return df_with_name.item() + "[" + str(part_id) + "]"
            return df_with_name.item()

        return get_field_instance_name


graph = Graph()
pd.set_option("display.max_rows", None, "display.max_columns", None)


# returns a graph containing columns of the same field
def get_field_plot(raw_id):
    node_id = NodeIdentifier(raw_id)
    filtered_data = DatasetGateway.submit(Query.from_identifier(node_id))
    # initialise figure
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    for col in filtered_data:
        trace = go.Violin(y=filtered_data[col],
                          name=col, box_visible=True,
                          line_color='black', meanline_visible=True,
                          fillcolor='lightseagreen', opacity=0.6)
        fig.add_trace(trace)
    fig.update_layout(title={
        'text': graph.get_field_name(node_id.field_id),
        'y': 0.85,
        'x': 0.475,
        'xanchor': 'center',
        'yanchor': 'top'
    },
        showlegend=False,
    )
    return fig
