import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc

contents_by_id = {
    "metadata": [
        html.H4("Plot", className="mb-3 graphs-card-title"),
        dcc.Graph(id="graph")
    ],
    "embedding": [
        html.H3("Embedding plot"),
        dcc.Graph(id="graph-embedding")
    ]
}

tabs = [
    dbc.Tabs([
        dbc.Tab(tab_id="metadata", label="Metadata plot"),
        dbc.Tab(tab_id="embedding", label="Embedding plot")
    ], id="graphs-tabs", card=True)
]

layout = dbc.Card(
    [
        dbc.CardHeader(tabs),
        dbc.CardBody([html.H4("Loading...")], id="graphs-card-body")
    ],
    style={"height": "34rem"},  # for dummy purposes, to remove later
)
