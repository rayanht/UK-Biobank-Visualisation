import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

import src.cards.settingscard_callbacks

layout = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H4("Settings", className="mb-3 settings-card-title"),
                html.Div(
                    [
                        html.H5("X-axis"),
                        html.H6("Variable"),
                        dcc.Dropdown(
                            id="variable-dropdown-x",
                            options=[],
                            placeholder="Select a variable to plot",
                            optionHeight=45,
                        ),
                        html.Div(
                            id="x-instance-selection-div",
                            children=[
                                html.H6("Instance"),
                                dcc.Dropdown(
                                    id="x-instance-options",
                                    options=[],
                                    placeholder="Select an instance",
                                    optionHeight=70,
                                ),
                            ],
                            style={"display": "none"},
                            className="mt-2",
                        ),
                        html.H5("Y-axis", className="mt-3"),
                        html.H6("Variable"),
                        dcc.Dropdown(
                            id="variable-dropdown-y",
                            options=[],
                            placeholder="Select a variable to plot",
                            optionHeight=45,
                            disabled=True,
                        ),
                        html.Div(
                            id="y-instance-selection-div",
                            children=[
                                html.H6("Instance"),
                                dcc.Dropdown(
                                    id="y-instance-options",
                                    options=[],
                                    placeholder="Select an instance",
                                    optionHeight=70,
                                ),
                            ],
                            style={"display": "none"},
                            className="mt-2",
                        ),
                        html.H5("Graph Type", className="mt-3"),
                        dcc.Dropdown(
                            id="settings-graph-type-dropdown",
                            options=[],
                            placeholder="Select a graph type",
                            clearable=False,
                            disabled=True,
                        ),
                        # TODO: Possibly delete this if client-side cache is implemented
                        # Hidden div inside the app that stores the intermediate value
                        html.Div(id="json_filtered_data", style={"display": "none"})
                        # html.H5("Y-Axis Instance", className="mt-2"),
                        # html.Div(id='y-instance-options-instr'),
                        # dcc.Dropdown(
                        #     id="y-instance-options",
                        #     placeholder="Select a y-axis variable to view instances",
                        #     # TODO: remove this when we are able to plot 2 variables at once (i.e. enable second variable)
                        #     disabled=True,
                        # ),
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
