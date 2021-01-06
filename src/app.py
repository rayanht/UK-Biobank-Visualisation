import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import layout.pages.index
import layout.pages.plotting_tool
from src.dash_app import app, dash

server = app.server

app.layout = html.Div(
    [dcc.Location(id="url", refresh=False, href="/plot"), html.Div(id="page-content")]
)


@app.callback(
    dash.dependencies.Output("page-content", "children"),
    [dash.dependencies.Input("url", "pathname")],
)
def display_page(pathname):
    if pathname == "/plot":
        return layout.pages.plotting_tool.layout
    else:
        return layout.pages.index.layout


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


collapsible_cards = ["tree", "settings", "analysis"]
collapsible_card_toggles = [
    "tree-collapse-toggle",
    "settings-collapse-toggle",
    "analysis-collapse-toggle",
    "tree-next-btn",
]


@app.callback(
    [Output(f"collapse-{i}", "is_open") for i in collapsible_cards],
    [Input(i, "n_clicks") for i in collapsible_card_toggles],
)
def toggle_accordion(n1, n2, n3, n4):
    ctx = dash.callback_context

    if not ctx.triggered:
        return True, False, False
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if (button_id == "settings-collapse-toggle" or button_id == "tree-next-btn") and (
        n2 or n4
    ):
        return False, True, False

    if button_id == "analysis-collapse-toggle" and n3:
        return False, False, True
    return True, False, False


if __name__ == "__main__":
    app.run_server(debug=True)
