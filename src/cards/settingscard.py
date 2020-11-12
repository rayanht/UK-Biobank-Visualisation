import dash_html_components as html
import dash_bootstrap_components as dbc

# Settings to be used
from src.setting.colour_setting import get_option_dropdown as get_colour_setting
from src.setting.instance_setting import get_option_dropdown as get_instance_setting
from src.setting.variable_setting import get_option_dropdown as get_variable_setting
from src.setting.filter_setting import get_option_dropdown as get_filter_setting
from src.setting.graph_type_setting import get_option_dropdown as get_graph_type_setting
from src.setting.plot_graph_setting import get_button as get_plot_graph_setting

# Function for selecting setting
def get_setting(encoding, arg=None):
    return _get_option_switcher[encoding](arg)

_get_option_switcher = {
    'colour': get_colour_setting,
    'instance': get_instance_setting,
    'variable': get_variable_setting,
    'filter': get_filter_setting,
    'graph_type': get_graph_type_setting,
    'plot_graph': get_plot_graph_setting,
}

# Actual settings card layout
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
                            get_setting('variable', 'x'),
                            get_setting('instance', 'x'),
                            get_setting('filter', 'x'),

                            html.H5("Y-axis", className="mt-3"),
                            html.H6("Variable"),
                            get_setting('variable', 'y'),
                            get_setting('instance', 'y'),
                            get_setting('filter', 'y'),

                            html.H5("Graph Type", className="mt-3"),
                            get_setting('graph_type'),
                            get_setting('colour'),
                        ],
                        className="flex-grow-1",
                        style={"overflow": "auto"},
                    ),
                    get_setting('plot_graph'),
                ],
                className="d-flex flex-column",
                style={"height": "41rem"},
            ),
            id=f"collapse-settings",
        ),
    ]
)
