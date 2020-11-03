import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash_extensions import Download
from dash_extensions.snippets import send_data_frame
from src.dash_app import app
from dash.dependencies import Input, Output
from src.selected_subset import SelectedSubset

download_icon = html.I(id="submit-button", n_clicks=0, className="fa fa-download")

subset = SelectedSubset()

layout = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H4("Plot", className="mb-3 graphs-card-title"),
                dcc.Graph(id="graph"),
                dbc.Button(
                    children=download_icon,
                    id="download-btn",
                    color="primary",
                    n_clicks=0,
                    disabled=True,
                ),
                dbc.Tooltip(
                    "Download plot as CSV",
                    target="download-btn",
                ),
                Download(id="download"),
            ]
        )
    ],
    style={"height": "36rem"},  # for dummy purposes, to remove later
)


@app.callback(Output("download", "data"), [Input("download-btn", "n_clicks")])
def generate_csv(n_clicks):
    if n_clicks > 0:
        return send_data_frame(
            subset.instance.data.to_csv,
            "ukbb_metadata_variable_subset.csv",
            index=False,
        )
