import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from src.graph import get_field_plot
from dash.dependencies import Input, Output, State
from src.dataset_gateway import field_id_meta_data
from src.graph import ValueType

from src.dash_app import app

layout = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H4("Settings", className="mb-3 settings-card-title"),
                html.Div(
                    [
                        html.H5("X-axis"),
                        dcc.Dropdown(
                            id="variable-dropdown-x",
                            options=[],
                            placeholder="Select a variable to plot",
                            optionHeight=45,
                        ),
                        html.H5("Y-axis", className="mt-2"),
                        dcc.Dropdown(
                            id="variable-dropdown-y",
                            options=[],
                            placeholder="Select a variable to plot",
                            optionHeight=45,
                            # TODO: remove this when we are able to plot 2 variables at once (i.e. enable second variable)
                            disabled=True,
                        ),
                        html.H5("Graph Type", className="mt-2"),
                        dcc.Dropdown(
                            id="settings-graph-type-dropdown",
                            options=[],
                            placeholder="Select a graph type",
                            clearable=False,
                            disabled=True,
                        ),
                    ],
                    className="flex-grow-1",
                    style={"overflow": "auto"},
                ),
                dbc.Button(
                    "Plot graph",
                    id="settings-card-submit",
                    color="primary",
                    className="mt-2",
                ),
            ],
            className="d-flex flex-column",
        )
    ],
    style={"height": "50rem"},  # for dummy purposes, to remove later
)

@app.callback(
    [
        Output(
            component_id="settings-graph-type-dropdown", component_property="options"
        ),
        Output(component_id="settings-graph-type-dropdown", component_property="value"),
        Output(
            component_id="settings-graph-type-dropdown", component_property="disabled"
        ),
    ],
    [Input(component_id="variable-dropdown-x", component_property="value")],
)
def update_graph_type(variable_dropdown_x):
    """Update the dropdown when nodes from the tree are selected"""
    if variable_dropdown_x is None:
        return [], None, True

    field_id = variable_dropdown_x  # Only supports one variable for now

    df = field_id_meta_data()
    value_type_id = int(df.loc[df["field_id"] == str(field_id)]["value_type"].values[0])
    value_type = ValueType(value_type_id)

    options = [
        {"label": "Violin", "value": 1},
        {"label": "Scatter", "value": 2},
        {"label": "Bar", "value": 3, "disabled": True},
        {"label": "Pie", "value": 4, "disabled": True},
    ]

    supported_graphs = value_type.supported_graphs

    graph_selection_list = []
    disabled_graphs = []

    for option in options:
        graph_type = option["value"]
        if graph_type in supported_graphs:
            graph_selection_list.append(option)
        else:
            option["disabled"] = True
            disabled_graphs.append(option)

    graph_selection_list.extend(disabled_graphs)

    return graph_selection_list, graph_selection_list[0]["value"], False


@app.callback(
    Output(component_id="graph", component_property="figure"),
    [Input(component_id="settings-card-submit", component_property="n_clicks")],
    [
        State(component_id="variable-dropdown-x", component_property="value"),
        State(component_id="settings-graph-type-dropdown", component_property="value"),
    ],
)
def update_graph(n, x_value, graph_type):
    """Update the graph when the dropdown selection changes"""
    if x_value is None:
        return {
            "layout": {
                "xaxis": {"visible": False},
                "yaxis": {"visible": False},
                "annotations": [
                    {
                        "text": "Select a data category to begin",
                        "xref": "paper",
                        "yref": "paper",
                        "showarrow": False,
                        "font": {"size": 22},
                    }
                ],
            }
        }
    return get_field_plot(x_value, graph_type)  # Plot first selected data
