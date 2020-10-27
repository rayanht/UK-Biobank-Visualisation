# -*- coding: utf-8 -*-

# Run this app with `gunicorn app:server` and
# visit http://127.0.0.1:8000/ in your web browser.
import os
import sys
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

sys.path.append(os.path.join(os.path.dirname(__file__), "hierarchy_tree"))

from src.dash_app import app
from src.cards import settingscard
from src.cards import treecard
from src.cards import graphscard
from src.cards import selectinstancecard

server = app.server

app.title = "UK BioBank Explorer"

colors = {"background": "#fdfdfd", "text": "#7FDBFF", "navbar-bg": "#f7f7f7"}

MAX_SELECTIONS = 30

navbar = dbc.Navbar(
    [
        dbc.NavbarBrand("UK BioBank Explorer", href="#"),
        dbc.NavbarToggler(id="navbar-toggler"),
        dbc.Collapse(
            dbc.Nav(
                [
                    dbc.NavItem(dbc.NavLink("Graphs", href="#")),  # dummy graphs link
                    dbc.DropdownMenu(  # dummy dropdown menu
                        children=[
                            dbc.DropdownMenuItem("Entry 1"),
                            dbc.DropdownMenuItem("Entry 2"),
                            dbc.DropdownMenuItem(divider=True),
                            dbc.DropdownMenuItem("Entry 3"),
                        ],
                        nav=True,
                        in_navbar=True,
                        label="Menu",
                        right=True,
                    ),
                ],
                className="ml-auto",
                navbar=True,
            ),
            id="navbar-collapse",
            navbar=True,
        ),
    ],
    className="px-5",
)

treeCard = treecard.layout

settingsCard = settingscard.layout

graphsCard = graphscard.layout

selectInstanceCard = selectinstancecard.layout

app.layout = html.Div(
    style={"backgroundColor": colors["background"], "height": "100vh"},
    children=[
        navbar,
        # row,
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(treeCard, width=4),  # Container for tree
                        dbc.Col(settingsCard, width=2),  # Container for settings
                        dbc.Col([selectInstanceCard, graphsCard], width=6),  # Container for graphs
                    ]
                ),
            ],
            style={"padding": "2.5rem 3rem 0rem 3rem"},
            fluid=True,
        ),
    ],
)


# we use a callback to toggle the collapse on small screens
@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open
