import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from src.graph import get_inst_names_options
from src.tree.node import NodeIdentifier

from src.dash_app import app
from dash.dependencies import Input, Output, State

layout = dbc.Card(
    [
        dbc.CardBody(
            id='select-instance-card',
            children=
            [
                html.H5("Select Instance", className="sel-instance-card-title"),
                dcc.Dropdown(id='x-instance-options'),
                html.Div(id='x-instance-options-instr')
            ],
        )
    ]
)

@app.callback(
    [Output(component_id='x-instance-options', component_property='options'),
    Output(component_id='x-instance-options', component_property='value')],
    [Input('variable-dropdown-x', 'value')],
)
def update_sel_inst_card(value) : 
    """Updating list of instances that may be selected"""
    if ((value == '') | (value is None)):
        return [], ''
    dict_with_inst = get_inst_names_options(value, False) # support only one variable for now
    options = [{'label': dict_with_inst[field_inst_id], 'value': field_inst_id} \
                for field_inst_id in dict_with_inst]
    return options, options[0]['value']

@app.callback(
    Output(component_id='x-instance-options-instr', component_property='children'),
    Input(component_id='x-instance-options', component_property='value')
)
def update_sel_inst_card_instr(value) :
    if (value == '') :
        return "Select an x-axis to view instances"
    else :
        return "Choose instance of field to plot on x-axis"
