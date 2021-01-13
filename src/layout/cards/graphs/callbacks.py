from dash.dependencies import Output, Input, State
from dash_extensions.snippets import send_data_frame

from graphs.view import contents
from src.dash_app import app

import pandas as pd


@app.callback(
    Output("graphs-card-body", "children"), [Input("graphs-tabs", "active_tab")]
)
def tab_contents(tab_id):
    """
    Callback to switch tabs based on user interaction in the graph section.
    Here we make all divs hidden and then unhide the one we're interested in.
    This is done to persist the plots when switching back and forth between
    tabs.

    :param tab_id: One of 'metadata', 'embedding' or 'clustering'
    :return: The HTML layout to display
    """
    tab_index = {"metadata": 0, "embedding": 1, "clustering": 2}[tab_id]
    new_content = contents.copy()
    for i in range(3):
        new_content[i].style = {"display": "None"}
    del new_content[tab_index].style
    return new_content


@app.callback(
    Output("download", "data"),
    [Input("download-btn", "n_clicks")],
    [State(component_id="graph", component_property="data")],
)
def generate_csv(n_clicks, plotted_data):
    """
    Callback to download graph data to a CSV file.

    :param n_clicks: number of times the download button was clicked.
                     Used here to simply detect if the button was clicked.
    :param plotted_data: the data that is currently displayed
    :return: an instruction for the browser to initiate a download of the
             DataFrame
    """
    if n_clicks:
        data = pd.read_json(plotted_data, orient="split")
        return send_data_frame(
            data.to_csv, "ukbb_metadata_variable_subset.csv", index=False
        )
