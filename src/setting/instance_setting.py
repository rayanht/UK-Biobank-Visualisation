import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Input, MATCH, Output
from src.dash_app import app
from src.graph import get_inst_names_options
from src.setting.variable_setting import get_dropdown_id as get_var_dropdown_id

def _prune_instance_label(label):
    # deletes everything after the year, which ends in a close parenthesis
    sep = ")"
    return label.split(sep, 1)[0] + sep


def _get_updated_instances(value):
    """Updating list of instances that may be selected"""
    if not value:
        return {"display": "none"}, [], ""

    dict_with_inst = get_inst_names_options(value)
    options = [
        {
            "label": _prune_instance_label(dict_with_inst[field_inst_id]),
            "value": field_inst_id,
        }
        for field_inst_id in dict_with_inst
    ]

    div_visible = {"display": "block"} if len(options) != 1 else {"display": "none"}

    return div_visible, options, options[0]["value"]  # select first instance by default


def get_option_dropdown(var: str):
    return html.Div(
                id={
                    'type': 'instance-selection-div',
                    'var': var,
                },
                children=[
                    html.H6("Instance"),
                    dcc.Dropdown(
                        id={
                            'type': 'instance-options',
                            'var': var,
                        },
                        options=[],
                        placeholder="Select an instance",
                        optionHeight=70,
                    ),
                ],
                style={"display": "none"},
                className="mt-2",
            )


def get_dropdown_id(var=MATCH):
    return {'var': var, 'type': 'instance-options'}

def get_div_id(var=MATCH):
    return {'var': var, 'type': 'instance-selection-div'}

@app.callback(
    [
        Output(component_id=get_div_id(), component_property="style"),
        Output(component_id=get_dropdown_id(), component_property="options"),
        Output(component_id=get_dropdown_id(), component_property="value"),
    ],
    [Input(component_id=get_var_dropdown_id(), component_property="value")],
)
def update_sel_inst(value):
    """Updating list of instances that may be selected"""
    return _get_updated_instances(value)
