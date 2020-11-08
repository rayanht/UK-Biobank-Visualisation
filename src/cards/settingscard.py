import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

import src.cards.settingscard_callbacks

layout = dbc.Card(
    [
        html.A(
            dbc.CardHeader(html.H5("Settings", className="ml-1")),
            id="settings-collapse-toggle",
        ),
        dbc.Collapse(
            dbc.CardBody(
                [
                    # html.H4("Settings", className="mb-3 settings-card-title"),
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
                            html.Div(
                                id="x-filter-slider-div",
                                children=[
                                    html.H6("Filter values", className="mt-2"),
                                    dcc.RangeSlider(
                                        id="x-filter-slider",
                                        allowCross=False,
                                        tooltip={
                                            "trigger": "hover",
                                            "placement": "bottom",
                                        },
                                    ),
                                ],
                                style={"display": "none"},
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
                            html.Div(
                                id="y-filter-slider-div",
                                children=[
                                    html.H6("Filter values", className="mt-2"),
                                    dcc.RangeSlider(
                                        id="y-filter-slider",
                                        allowCross=False,
                                        tooltip={
                                            "trigger": "hover",
                                            "placement": "bottom",
                                        },
                                    ),
                                ],
                                style={"display": "none"},
                            ),
                            html.H5("Graph Type", className="mt-3"),
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
                style={"height": "41rem"},
            ),
            id=f"collapse-settings",
        ),
    ]
)
