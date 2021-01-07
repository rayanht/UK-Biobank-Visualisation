import dash_html_components as html
import dash_bootstrap_components as dbc

from src.layout.cards.settings.callbacks import get_setting

# Actual settings card layout
layout = dbc.Card(
    [
        html.A(
            dbc.CardHeader(html.H5("Plot", className="ml-1")),
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
                            get_setting("variable", "x"),
                            get_setting("instance", "x"),
                            get_setting("filter", "x"),
                            html.H5("Y-axis", className="mt-3"),
                            html.H6("Variable"),
                            get_setting("variable", "y"),
                            get_setting("instance", "y"),
                            get_setting("filter", "y"),
                            html.H5("Graph Type", className="mt-3"),
                            get_setting("graph_type"),
                            html.H6("Trendline", className="mt-3"),
                            get_setting("trendline"),
                            get_setting("colour"),
                            get_setting("instance", "colour"),
                        ],
                        className="flex-grow-1",
                        style={"overflow": "auto"},
                    ),
                    get_setting("plot_graph"),
                ],
                className="d-flex flex-column",
                style={"height": "41rem"},
            ),
            id=f"collapse-settings",
        ),
    ]
)
