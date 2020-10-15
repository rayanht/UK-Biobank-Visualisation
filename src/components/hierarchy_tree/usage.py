import hierarchy_tree
import dash
from dash.dependencies import Input, Output
import dash_html_components as html

app = dash.Dash(__name__)

app.layout = html.Div([
    hierarchy_tree.HierarchyTree(
        id='input'),
    html.Div(id='output')
])


if __name__ == '__main__':
    app.run_server(debug=True)
