import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc

layout = dbc.Card(
    [
        dbc.CardBody(
            [html.H4("Plot", className="mb-3 graphs-card-title"), dcc.Graph(id="graph")]
        )
    ],
    style={"height": "34rem"},  # for dummy purposes, to remove later
)
