import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from src.graph import get_inst_names_options

from src.dash_app import app
from dash.dependencies import Input, Output, State

layout = dbc.Card(
    [
        dbc.CardBody(
            id='select-instance-card',
            children=
            [
                html.H4("Select Instance", className="mb-3 settings-card-title"),
                html.H5("X-Axis Instance", className="mt-2"),
                html.Div(id='x-instance-options-instr'),
                dcc.Dropdown(
                    id='x-instance-options',
                    placeholder="Select an x-axis variable to view instances",
                ),
                html.H5("Y-Axis Instance", className="mt-2"),
                html.Div(id='y-instance-options-instr'),
                dcc.Dropdown(
                    id="y-instance-options",
                    placeholder="Select a y-axis variable to view instances",
                    # TODO: remove this when we are able to plot 2 variables at once (i.e. enable second variable)
                    disabled=True,
                ),
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
def update_x_sel_inst(n, x_value) :
    """Updating list of instances that may be selected on x-axis"""
    if ((x_value == '') | (x_value is None)):
        return [], ''
    dict_with_inst = get_inst_names_options(x_value, False)
    options = [{'label': dict_with_inst[field_inst_id], 'value': field_inst_id} \
                for field_inst_id in dict_with_inst]
    return options, options[0]['value'] # select first instance by default

@app.callback(
    Output(component_id='x-instance-options-instr', component_property='children'),
    Input(component_id='x-instance-options', component_property='value')
)
def update_x_sel_inst_instr(x_value) :
    """Update description of x-axis variable instance box"""
    if (x_value != '') :
        return "Choose other instances of field to plot on x-axis"

@app.callback(
    [Output(component_id='y-instance-options', component_property='options'),
    Output(component_id='y-instance-options', component_property='value')],
    [Input(component_id="settings-card-submit", component_property="n_clicks")],
    [State(component_id='variable-dropdown-y', component_property='value')],
)
def update_y_sel_inst(n, y_value) :
    """Updating list of instances that may be selected on y-axis"""
    if ((y_value == '') | (y_value is None)):
        return [], ''
    dict_with_inst = get_inst_names_options(y_value, False)
    options = [{'label': dict_with_inst[field_inst_id], 'value': field_inst_id} \
                for field_inst_id in dict_with_inst]
    return options, options[0]['value'] # select first instance by default

@app.callback(
    Output(component_id='y-instance-options-instr', component_property='children'),
    Input(component_id='y-instance-options', component_property='value')
)
def update_y_sel_inst_instr(y_value) :
    """Update description of y-axis variable instance box"""
    if (y_value != '') :
        return "Choose other instances of field to plot on y-axis"
