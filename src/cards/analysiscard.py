import inspect
import numpy as np
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from sklearn.manifold import TSNE
from umap import UMAP
import pandas as pd
from src.dash_app import app
from src.dataset_gateway import DatasetGateway, Query
from src.setting.instance_setting import _get_updated_instances
from src.setting.variable_setting import get_dropdown_id
from src.tree.node import NodeIdentifier
import plotly.express as px

tsne_epoch_slider = dbc.FormGroup(
    [
        dbc.Label("Number of epochs"),
        dcc.Slider(
            id="tsne-epoch-slider",
            min=250,
            max=3000,
            step=10,
            value=1000,
            tooltip={"always_visible": True, "placement": "bottom"},
        ),
        dbc.FormText(
            "Maximum number of iterations for the optimisation.", color="secondary"
        ),
    ]
)

tsne_learning_rate_slider = dbc.FormGroup(
    [
        dbc.Label("Learning Rate"),
        dcc.Slider(
            id="tsne-learning-rate-slider",
            min=10,
            max=1000,
            step=1,
            value=200,
            tooltip={"always_visible": True, "placement": "bottom"},
        ),
        dbc.FormText(
            "The learning rate for t-SNE is usually in the range [10.0, 1000.0]. If the learning rate is too high, "
            "the data may look like a ‘ball’ with any point approximately equidistant from its nearest neighbours. If "
            "the learning rate is too low, most points may look compressed in a dense cloud with few outliers. If the "
            "cost function gets stuck in a bad local minimum increasing the learning rate may help.",
            color="secondary",
        ),
    ]
)

tsne_perplexity_slider = dbc.FormGroup(
    [
        dbc.Label("Perplexity"),
        dcc.Slider(
            id="tsne-perplexity-slider",
            min=5,
            max=100,
            step=1,
            value=10,
            tooltip={"always_visible": True, "placement": "bottom"},
        ),
        dbc.FormText(
            "The perplexity is related to the number of nearest neighbors that is used in other manifold learning "
            "algorithms. Larger datasets usually require a larger perplexity. Consider selecting a value between 5 "
            "and 50.",
            color="secondary",
        ),
    ]
)

tsne_dimensionality_slider = dbc.FormGroup(
    [
        dbc.Label("Output Dimension"),
        dcc.Slider(
            id="tsne-dimension-slider",
            min=2,
            max=3,
            step=1,
            value=2,
            tooltip={"always_visible": True, "placement": "bottom"},
        ),
        dbc.FormText(
            "Controls the dimensionality of the reduced output dimension space.",
            color="secondary",
        ),
    ]
)

tsne_metric_dropdown = dbc.FormGroup(
    [
        dbc.Label("Metric"),
        dcc.Dropdown(
            id="tsne-metric-dropdown",
            options=[
                {"label": "Euclidean", "value": "euclidean"},
                {"label": "Manhattan", "value": "manhattan"},
                {"label": "Cosine", "value": "cosine"},
                {"label": "Haversine", "value": "haversine"},
            ],
            value="euclidean",
        ),
        dbc.FormText(
            "Controls how distance is computed in the ambient space of the input data.",
            color="secondary",
        ),
    ]
)

umap_dimensionality_slider = dbc.FormGroup(
    [
        dbc.Label("Output Dimension"),
        dcc.Slider(
            id="umap-dimension-slider",
            min=1,
            max=3,
            step=1,
            value=2,
            tooltip={"always_visible": True, "placement": "bottom"},
        ),
        dbc.FormText(
            "Controls the dimensionality of the reduced output dimension space. For visualisation purposes, "
            "in the case of a 1D UMAP, data will be randomly distributed on the y-axis to provide some "
            "separation between points.",
            color="secondary",
        ),
    ]
)

umap_metric_dropdown = dbc.FormGroup(
    [
        dbc.Label("Metric"),
        dcc.Dropdown(
            id="umap-metric-dropdown",
            options=[
                {"label": "Euclidean", "value": "euclidean"},
                {"label": "Manhattan", "value": "manhattan"},
                {"label": "Chebyshev", "value": "chebyshev"},
                {"label": "Minkowski", "value": "minkowski"},
            ],
            value="euclidean",
        ),
        dbc.FormText(
            "Controls how distance is computed in the ambient space of the input data.",
            color="secondary",
        ),
    ]
)

umap_neighbours_slider = dbc.FormGroup(
    [
        dbc.Label("Neighbours"),
        dcc.Slider(
            id="umap-neighbours-slider",
            min=0,
            max=2000,
            step=1,
            value=10,
            tooltip={"always_visible": True, "placement": "bottom"},
        ),
        dbc.FormText(
            "The number of nearest neighbours used to compute the fuzzy simplical set, which is used to approximate "
            "the shape of the manifold.",
            color="secondary",
        ),
    ]
)

tabs = [
    dbc.Tabs(
        [
            dbc.Tab(tab_id="dimensionality", label="Dimensionality Reduction"),
            dbc.Tab(tab_id="clustering", label="Clustering"),
        ],
        id="analysis-tabs",
        card=True,
    )
]

dimensionality_tabs = [
    dbc.Tabs(
        [
            dbc.Tab(tab_id="UMAP", label="UMAP"),
            dbc.Tab(tab_id="t-SNE", label="t-SNE"),
            dbc.Tab(tab_id="PCA", label="PCA"),
        ],
        id="dimensionality-tabs",
        card=True,
        active_tab="UMAP",
    )
]

dimensionality_tab_content = {
    "PCA": [html.Div([html.H5("PCA")])],
    "t-SNE": [
        dbc.Form(
            [
                tsne_metric_dropdown,
                tsne_dimensionality_slider,
                tsne_perplexity_slider,
                tsne_learning_rate_slider,
                tsne_epoch_slider,
            ]
        ),
        dbc.Button("Run", color="primary", block=True, id="run-tsne"),
    ],
    "UMAP": [
        dbc.Form(
            [umap_metric_dropdown, umap_dimensionality_slider, umap_neighbours_slider]
        ),
        dbc.Button("Run", color="primary", block=True, id="run-umap"),
    ],
}

analysis_tab_content = {
    "dimensionality": [
        html.Div(
            [
                dbc.FormGroup(
                    [
                        dbc.Label("Data fields"),
                        dcc.Dropdown(
                            id={"var": "all", "type": "variable-dropdown"},
                            options=[],
                            multi=True,
                        ),
                    ]
                ),
                dbc.FormGroup(
                    [
                        dbc.Label("Sample size"),
                        dcc.Slider(
                            id="sample-size-slider",
                            min=3.7,
                            max=5.7,
                            step=None,
                            marks={
                                3.7: "5k",
                                4: "10k",
                                4.4: "25k",
                                4.7: "50k",
                                5: "100k",
                                5.4: "250k",
                                5.7: "500k",
                            },
                            value=3.7,
                        ),
                        dbc.FormText(
                            "Controls what fraction of the dataset is used in order to generate the embeddings. Try "
                            "reducing this number if the plots are too dense or increasing it if they are too sparse."
                        ),
                    ]
                ),
                dbc.Card(
                    children=[
                        dbc.CardHeader(dimensionality_tabs),
                        dbc.CardBody(
                            children=dimensionality_tab_content["UMAP"],
                            id="dimensionality-card-body",
                        ),
                    ]
                ),
            ]
        )
    ],
    "clustering": [html.Div([html.H5("Clustering")])],
}

layout = dbc.Card(
    [
        html.A(
            dbc.CardHeader(html.H5("Analysis Settings", className="ml-1")),
            id="analysis-collapse-toggle",
        ),
        dbc.Collapse(
            dbc.CardBody(
                dbc.Card(
                    children=[
                        dbc.CardHeader(tabs),
                        dbc.CardBody(
                            children=analysis_tab_content["dimensionality"],
                            id="analysis-card-body",
                        ),
                    ]
                )
            ),
            id=f"collapse-analysis",
        ),
    ]
)


@app.callback(
    Output("analysis-card-body", "children"), [Input("analysis-tabs", "active_tab")]
)
def tab_contents_analysis(tab_id):
    return analysis_tab_content[tab_id]


@app.callback(
    Output("dimensionality-card-body", "children"),
    [Input("dimensionality-tabs", "active_tab")],
)
def tab_contents_dimensionality(tab_id):
    return dimensionality_tab_content[tab_id]


def compute_embedding(dimensions, sample_size, selected, estimator):
    corrected_sample_size = int(10 ** sample_size)
    selected = [_get_updated_instances(var["value"])[2] for var in selected]
    identifiers = list(map(NodeIdentifier, selected))
    features = DatasetGateway.submit(
        Query.from_identifiers(identifiers).limit_output(corrected_sample_size)
    )
    features = features.replace(r"^\s*$", np.nan, regex=True).dropna()
    features = features.drop(features[features.eid == "eid"].index)
    projection = estimator.fit_transform(features.iloc[:, 1:].to_numpy())
    if dimensions == 3:
        fig = px.scatter_3d(projection, x=0, y=1, z=2)
    else:
        fig = px.scatter(projection, x=0, y=1)
    return fig


tsne_state = []

umap_state = []


@app.callback(
    [Output(component_id="analysis-card", component_property="children")],
    [Input(component_id="run-umap", component_property="n_clicks")],
    [
        State(component_id="umap-metric-dropdown", component_property="value"),
        State(component_id="umap-dimension-slider", component_property="value"),
        State(component_id="umap-neighbours-slider", component_property="value"),
        State(component_id=get_dropdown_id("all"), component_property="options"),
        State(component_id="sample-size-slider", component_property="value"),
    ],
    prevent_initial_call=True,
)
def umap(n, metric, dimensions, neighbours, selected, sample_size):
    ctx = dash.callback_context
    print(ctx.triggered)
    if ctx.triggered[0]["value"] is None or not selected:
        return dash.no_update
    else:
        estimator = UMAP(
            n_components=dimensions,
            init="random",
            random_state=0,
            metric=metric,
            n_neighbors=neighbours,
        )
        return [
            dcc.Graph(
                figure=compute_embedding(dimensions, sample_size, selected, estimator)
            )
        ]


@app.callback(
    [Output(component_id="analysis-graph", component_property="figure")],
    [Input(component_id="run-tsne", component_property="n_clicks")],
    [
        State(component_id="tsne-metric-dropdown", component_property="value"),
        State(component_id="tsne-dimension-slider", component_property="value"),
        State(component_id="tsne-perplexity-slider", component_property="value"),
        State(component_id="tsne-learning-rate-slider", component_property="value"),
        State(component_id="tsne-epoch-slider", component_property="value"),
        State(component_id=get_dropdown_id("all"), component_property="options"),
        State(component_id="sample-size-slider", component_property="value"),
    ],
    prevent_initial_call=True,
)
def tsne(
    n, metric, dimensions, perplexity, learning_rate, epochs, selected, sample_size
):
    ctx = dash.callback_context
    print(ctx.triggered)
    if ctx.triggered[0]["value"] is None or not selected:
        return dash.no_update
    else:
        estimator = TSNE(
            n_components=dimensions,
            random_state=0,
            metric=metric,
            perplexity=perplexity,
            learning_rate=learning_rate,
            n_iter=epochs,
        )
        return [compute_embedding(dimensions, sample_size, selected, estimator)]
