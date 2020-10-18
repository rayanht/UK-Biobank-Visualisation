import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import os 
import re

from src.dataset import get_field_names_to_inst
from src.dataset import get_meta_data

class Graph:

    def __init__(self) :
        self.meta_data = get_meta_data()
        self.field_names_to_inst = get_field_names_to_inst()
        self.field_names_to_ids \
            = self.field_names_to_inst.loc[self.field_names_to_inst['InstanceID'].isnull()]\
                [['FieldID', 'NodeName']].dropna(how='any', axis=0)

    # get field id from <field_id>-<instance>.<part>
    def get_field_id(self, meta_id_inst):
        return int(re.split("-|\.", str(meta_id_inst))[0])

    # get instance id from <field_id>-<instance>.<part>
    def get_inst_id(self, meta_id) :
        return int(re.split("-|\.", str(meta_id))[1])

    # get part id from <field_id>-<instance>.<part>
    def get_part_id(self, meta_id) :
        return int(re.split("-|\.", str(meta_id))[2])

    def hasArrayItems(self, meta_ids) :
        if (len(meta_ids) <= 1):
            return False
        return self.get_part_id(meta_ids[0]) != self.get_part_id(meta_ids[1])

    def get_field_name(self, id) :
        return self.field_names_to_ids.loc[self.field_names_to_ids['FieldID'] == id, 'NodeName'].item()

    def get_field_instance_map(self, hasArrayItems) :
        def get_field_instance_name(meta_id) :
            field_id = self.get_field_id(meta_id)
            inst_id = self.get_inst_id(meta_id)
            df_with_name = self.field_names_to_inst.loc[\
                (self.field_names_to_inst['FieldID'] == field_id) & \
                    (self.field_names_to_inst['InstanceID'] == inst_id)\
                ]['NodeName']
            if (hasArrayItems) :
                part_id = self.get_part_id(meta_id)
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
        has_array = self.hasArrayItems(list(filtered_data.columns))
        filtered_data.rename(mapper=self.get_field_instance_map(has_array), axis='columns', inplace=True)
        return filtered_data

graph = Graph()
pd.set_option("display.max_rows", None, "display.max_columns", None)

# returns a graph containing columns of the same field
def get_field_plot(id, isMetaId=True) :
    field_id = graph.get_field_id(id) if isMetaId else id
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
        