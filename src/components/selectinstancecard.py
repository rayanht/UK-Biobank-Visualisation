import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from src.graph import get_inst_names_options
from src.tree.node import NodeIdentifier

def update_sel_inst_card(value) : 
    if (value == ''):
        return [], ''
    dict_with_inst = get_inst_names_options(value, False) # support only one variable for now
    options = [{'label': dict_with_inst[field_inst_id], 'value': field_inst_id} \
                for field_inst_id in dict_with_inst]
    return options, options[0]['value']