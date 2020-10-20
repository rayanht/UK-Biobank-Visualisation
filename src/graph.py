import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import re

from src.dataset import get_field_names_to_inst
from src.dataset import get_meta_data

# get field id from <field_id>-<instance>.<part>
def get_field_id(meta_id):
    return int(re.split("-|\.", str(meta_id))[0])

# get instance id from <field_id>-<instance>.<part>
def get_inst_id(meta_id) :
    return int(re.split("-|\.", str(meta_id))[1])

# get part id from <field_id>-<instance>.<part>
def get_part_id(meta_id) :
    return int(re.split("-|\.", str(meta_id))[2])

def has_multiple_instances(meta_ids) :
    if (len(meta_ids) <= 1):
        return False
    return get_inst_id(meta_ids[0]) != get_inst_id(meta_ids[1])

def has_array_items(meta_ids) :
    if (len(meta_ids) <= 1):
        return False
    return get_part_id(meta_ids[0]) != get_part_id(meta_ids[1])

class Graph:

    def __init__(self) :
        self.meta_data = get_meta_data()
        self.field_names_to_inst = get_field_names_to_inst()
        self.field_names_to_ids \
            = self.field_names_to_inst.loc[self.field_names_to_inst['InstanceID'].isnull()]\
                [['FieldID', 'NodeName']].dropna(how='any', axis=0)

    def get_field_name(self, field_id) :
        return self.field_names_to_ids.loc[self.field_names_to_ids['FieldID'] == field_id, 'NodeName'].item()

    def get_field_instance_map(self, has_instances, has_array) :
        def get_field_instance_name(meta_id) :
            field_id = get_field_id(meta_id)
            inst_id = get_inst_id(meta_id)
            df_with_name \
                = self.field_names_to_inst.loc[\
                    (self.field_names_to_inst['FieldID'] == field_id) & \
                    (self.field_names_to_inst['InstanceID'] == inst_id)\
                    ]['NodeName'] \
                if has_instances else \
                    self.field_names_to_inst.loc[\
                    (self.field_names_to_inst['FieldID'] == field_id)]['NodeName']
            if (has_array) :
                part_id = get_part_id(meta_id)
                return df_with_name.item() + "[" + str(part_id) + "]"
            return df_with_name.item()
        return get_field_instance_name

    # get all columns of the same field
    def get_field_data(self, field_id, dropAny=False) :
        filtered_data = self.meta_data.loc[:, \
                            self.meta_data.columns.str.startswith(str(field_id) + '-')]. \
                                dropna(how='all', axis=0). \
                                dropna(how='all', axis=1)
        if dropAny:
            filtered_data.dropna(how='any', axis=0, inplace=True)
        else:
            filtered_data.dropna(how='all', axis=0, inplace=True)
        filtered_meta_ids = list(filtered_data.columns)
        has_array = has_array_items(filtered_meta_ids)
        has_instances = has_multiple_instances(filtered_meta_ids)
        filtered_data.rename(mapper=self.get_field_instance_map(has_instances, has_array), \
                             axis='columns', inplace=True)
        return filtered_data

graph = Graph()
pd.set_option("display.max_rows", None, "display.max_columns", None)

# returns a graph containing columns of the same field
def get_field_plot(raw_id, isMetaId=True) :
    field_id = get_field_id(raw_id) if isMetaId else raw_id
    field_name = graph.get_field_name(field_id)
    filtered_data = graph.get_field_data(field_id)
    # initialise figure
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    for col in filtered_data:
        trace = go.Violin(y=filtered_data[col],
                            name=col, box_visible=True,
                            line_color='black', meanline_visible=True,
                            fillcolor='lightseagreen', opacity=0.6)
        fig.add_trace(trace)
    fig.update_layout(title={
        'text': field_name,
        'y':0.85,
        'x':0.475,
        'xanchor': 'center',
        'yanchor': 'top'
        },
        showlegend=False,
    )
    return fig
        