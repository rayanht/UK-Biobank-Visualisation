import dash
import dash_html_components as html

from src.components.hierarchy_tree.hierarchy_tree.HierarchyTree import HierarchyTree

app = dash.Dash(__name__)

app.layout = html.Div([
    HierarchyTree(
        id='input'),
    html.Div(id='output')
])

if __name__ == '__main__':
    app.run_server(debug=True)
