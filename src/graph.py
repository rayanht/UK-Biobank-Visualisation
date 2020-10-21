import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.dataset_gateway import DatasetGateway, Query
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

    def get_field_name(self, field_id):
        return self.field_names_to_ids.loc[
            self.field_names_to_ids["FieldID"] == field_id, "NodeName"
        ].item()

    def get_inst_name_dict(self, field_id) :
        inst_names = self.field_names_to_inst.loc[\
                        self.field_names_to_inst['FieldID'] == int(field_id)]
        if (len(inst_names) > 1) :
            # There are multiple instances. Drop row with field name
            inst_names = inst_names.loc[inst_names['InstanceID'].notnull()]
            inst_names['dbid'] \
                = inst_names.apply(lambda row:  f'_{field_id}_{int(row.InstanceID)}_0_', axis=1)
        else :
            inst_names['dbid'] = '_' + field_id + '_0_0'
        inst_name_dict = dict(zip(inst_names['dbid'], inst_names['NodeName']))
        return inst_name_dict

    def get_field_instance_map(self, has_instances, has_array):
        def get_field_instance_name(meta_id):
            meta_id = NodeIdentifier(meta_id)
            field_id = meta_id.field_id
            inst_id = meta_id.instance_id
            df_with_name = (
                self.field_names_to_inst.loc[
                    (self.field_names_to_inst["FieldID"] == field_id)
                    & (self.field_names_to_inst["InstanceID"] == inst_id)
                ]["NodeName"]
                if has_instances
                else self.field_names_to_inst.loc[
                    (self.field_names_to_inst["FieldID"] == field_id)
                ]["NodeName"]
            )
            if has_array:
                part_id = meta_id.part_id
                return df_with_name.item() + "[" + str(part_id) + "]"
            return df_with_name.item()

        return get_field_instance_name

    # get columns of all parts of an instance of a field
    def get_inst_data(self, field_inst_id_str, dropAny=False) :
        # fetch columns with corresponding field id and instance id
        filtered_data = self.meta_data.loc[:, \
                            self.meta_data.columns.str.\
                                startswith(field_inst_id_str + '.')].\
                                dropna(how='all', axis=1)

        # drop null values
        if dropAny:
            filtered_data.dropna(how='any', axis=0, inplace=True)
        else:
            filtered_data.dropna(how='all', axis=0, inplace=True)

        # rename columns
        has_array = has_array_items(list(filtered_data.columns)) 
        filtered_data.rename(mapper=self.get_field_instance_map(has_array), axis='columns', inplace=True)
        return filtered_data

graph = Graph()
pd.set_option("display.max_rows", None, "display.max_columns", None)

# returns a graph containing columns of the same field
def get_field_plot(raw_id):
    node_id = NodeIdentifier(raw_id)
    filtered_data = DatasetGateway.submit(Query.from_identifier(node_id))
    # initialise figure
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
    fig.update_layout(
        title={
            "text": graph.get_field_name(node_id.field_id),
            "y": 0.85,
            "x": 0.475,
            "xanchor": "center",
            "yanchor": "top",
        },
        showlegend=False,
    )
    return fig


# returns a dict of options for a dropdown list of instances
def get_inst_names_options(raw_id, isMetaId=True) :
    field_id = NodeIdentifier(raw_id).field_id
    return graph.get_inst_name_dict(field_id)
