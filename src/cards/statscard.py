import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc

layout = dbc.Card(
    dcc.Loading(
        [
            html.H4("Summary statistics", className="summary-stats-title"),
            dbc.Table(id="statistics", size="sm")
        ]
    ),
    style={"height": "15rem", "width": "100%",
            "overflowX": "scroll", 'overflowY': 'scroll'},
    body=True,
)
