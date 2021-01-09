import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import src.layout.cards.analysis
import src.layout.cards.settings
import src.layout.cards.stats
import src.layout.cards.tree
import src.layout.cards.graphs

colors = {"background": "#fdfdfd", "text": "#7FDBFF", "navbar-bg": "#f7f7f7"}

tree_card = src.layout.cards.tree.layout
plot_settings_card = src.layout.cards.settings.layout
analysis_card = src.layout.cards.analysis.layout
graphs_card = src.layout.cards.graphs.layout
stats_card = src.layout.cards.stats.layout

navbar = dbc.Navbar(
    [dbc.NavbarBrand("UK Biobank Explorer", href="/")], className="px-5"
)

layout = html.Div(
    style={"backgroundColor": colors["background"], "height": "100vh"},
    children=[
        navbar,
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                [tree_card, plot_settings_card, analysis_card],
                                className="accordion",
                            ),
                            width=5,
                        ),
                        dbc.Col(
                            children=[
                                dbc.Row(dbc.Col(graphs_card)),
                                # Container for graphs
                                dbc.Row(
                                    dbc.Col(
                                        stats_card,
                                        # Container for summary statistics
                                        style={"height": "auto"},
                                    ),
                                    className="mt-3",
                                ),
                                html.Div(id="signal", style={"display": "none"}),
                            ],
                            width=7,
                        ),
                    ]
                )
            ],
            style={"padding": "2.5rem 3rem 2.5rem 3rem"},
            fluid=True,
        ),
    ],
)
