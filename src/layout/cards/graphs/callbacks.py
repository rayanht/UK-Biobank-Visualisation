from dash.dependencies import Output, Input, State
from dash_extensions.snippets import send_data_frame

from dash_app import app
from graphs.view import contents_by_id

import pandas as pd


@app.callback(
    Output("graphs-card-body", "children"), [Input("graphs-tabs", "active_tab")]
)
def tab_contents(tab_id):
    return contents_by_id[tab_id]


@app.callback(
    Output("download", "data"),
    [Input("download-btn", "n_clicks")],
    [State(component_id="plotted-data", component_property="data")],
)
def generate_csv(n_clicks, plotted_data):
    if n_clicks:
        data = pd.read_json(plotted_data, orient="split")
        return send_data_frame(
            data.to_csv, "ukbb_metadata_variable_subset.csv", index=False
        )
