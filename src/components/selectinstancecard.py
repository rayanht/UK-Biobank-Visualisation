import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from src.graph import get_inst_names_options
from src.tree.node import NodeIdentifier

def update_sel_inst_card(n, selected) : 
    if (len(selected) == 0):
        return []
    print("Updating instance selection card.")
    dict_with_inst = get_inst_names_options(selected[0], False) # support only one variable for now
    options = [{'label': dict_with_inst[field_inst_id], 'value': field_inst_id} \
                for field_inst_id in dict_with_inst]
    print("The full list of instances is ", options)
    print("The default value is ", NodeIdentifier(selected[0]).db_id())
    return [
        dbc.CardBody(
            [
                html.H5("Select Instance", className="sel-instance-card-title"),
                dcc.Dropdown(
                    id='instance-names',
                    options=options,
                    value=NodeIdentifier(selected[0]).db_id()
                ),
            ]
        )
    ]