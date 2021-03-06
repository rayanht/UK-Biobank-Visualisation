from dash.dependencies import Input, Output, State

from src.dash_app import app
from src.layout.cards.tree.view import explore_tab_content
from src.tree.node_utils import filter_hierarchy


@app.callback(
    Output("explore-card-body", "children"), [Input("explore-tabs", "active_tab")]
)
def tab_contents_analysis(tab_id):
    """
    Callback to switch tabs based on user interaction in the explore accordion

    :param tab_id: One of 'tree' or 'save'
    :return: The HTML layout to display
    """
    return explore_tab_content[tab_id]


@app.callback(
    Output("save-selection-modal", "is_open"),
    [Input("save-selection-btn", "n_clicks"), Input("close", "n_clicks")],
    [State("save-selection-modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open
