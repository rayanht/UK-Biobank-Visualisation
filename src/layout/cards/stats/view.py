import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc

layout = dbc.Card(
    dcc.Loading(
        [
            html.H4("Summary statistics", className="summary-stats-title"),
            dbc.Table(id="statistics", size="sm"),
        ],
        style={"margin-top": "150px"},
    ),
    style={
        "height": "15rem",
        "width": "100%",
        "flex-direction": "column",
        "overflowX": "auto",
        "overflowY": "auto",
    },
    body=True,
)
