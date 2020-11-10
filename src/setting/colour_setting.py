import dash_core_components as dcc
import dash_html_components as html

from src.tree.node_utils import is_leaf, is_sex_option, get_option
from dash.dependencies import Input, Output, State
from src.dash_app import app


def get_option_dropdown(arg):
    return html.Div(    
                id="colour-selection-div",
                children=[
                    dcc.Store(id="colour-options"),
                    html.H6("Colour", className="mt-2"),
                    dcc.Dropdown(
                        id="settings-graph-colour-dropdown",
                        options=[],
                        placeholder="Optional: Group data by category",
                        clearable=True,
                        optionHeight=70,
                    ),
                ],
                style={"display": "none"},
            )

# Callback for updating colour options
@app.callback(
    [
        Output(component_id="colour-options", component_property="data"),
        Output(component_id="colour-selection-div", component_property="style"),
        Output(component_id="settings-graph-colour-dropdown", component_property="options"),
        Output(component_id="settings-graph-colour-dropdown", component_property="value"),
    ],
    [
        Input(component_id="tree", component_property="data"),
        Input(component_id="settings-graph-type-dropdown", component_property="value"),
    ],
    State(component_id="colour-options", component_property="data"),
)
def get_baseline_nodes(hierarchy, graph_type, cached_colour_options):
    """Updates colour options with baselines characteristic nodes after tree has been loaded"""
    if ((graph_type == 4) | (graph_type == None)):
        # Currently do not support colour for pie charts
        return None, {"display": "none"}, [], None
    
    if (cached_colour_options == None):
        baseline_children = hierarchy[0]['childNodes'][0]['childNodes']
        leaf_baseline = [child for child in baseline_children if is_leaf(child)]
        cached_colour_options = [get_option(node) for node in leaf_baseline]

    options = cached_colour_options
    if (graph_type == 1):
        # Violin plot can only use Sex as colour argument
        options = [option for option in options if is_sex_option(option)]
    return cached_colour_options, {"display": "block"}, options, None