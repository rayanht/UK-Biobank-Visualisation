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
    [Input(component_id="settings-card-submit", component_property="n_clicks")],
    [State(component_id='variable-dropdown-x', component_property='value')],
)
def update_sel_inst_card(n, x_value) : 
    """Updating list of instances that may be selected"""
    if ((x_value == '') | (x_value is None)):
        return [], ''
    dict_with_inst = get_inst_names_options(x_value, False) # support only one variable for now
    options = [{'label': dict_with_inst[field_inst_id], 'value': field_inst_id} \
                for field_inst_id in dict_with_inst]
    return options, options[0]['value']

@app.callback(
    Output(component_id='x-instance-options-instr', component_property='children'),
    Input(component_id='x-instance-options', component_property='value')
)
def update_sel_inst_card_instr(x_value) :
    """Updating description of x-axis variable instance box"""
    if (x_value == '') :
        return "Select an x-axis to view instances"
    else :
        return "Choose other instances of field to plot on x-axis"
