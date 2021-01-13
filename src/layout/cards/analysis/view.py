import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from src.dash_app import app

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
            "The perplexity is related to the number of nearest neighbors "
            "that is used in other manifold learning algorithms. Larger "
            "datasets usually require a larger perplexity. Consider selecting "
            "a value between 5 and 50.",
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
k_means_k_slider = dbc.FormGroup(
    [
        dbc.Label("Number of clusters"),
        dcc.Slider(
            id="k-means-k-slider",
            min=2,
            max=50,
            step=1,
            value=8,
            tooltip={"always_visible": True, "placement": "bottom"},
        ),
        dbc.FormText(
            "The number of clusters to form as well as the number of centroids to generate.",
            color="secondary",
        ),
    ]
)

k_means_n_init_slider = dbc.FormGroup(
    [
        dbc.Label("Number of runs"),
        dcc.Slider(
            id="k-means-n-init-slider",
            min=1,
            max=20,
            step=1,
            value=10,
            tooltip={"always_visible": True, "placement": "bottom"},
        ),
        dbc.FormText(
            "Number of time the k-means algorithm will be run with different "
            "centroid seeds. The final results will be the best output of "
            "n consecutive runs in terms of inertia.",
            color="secondary",
        ),
    ]
)

k_means_max_epoch_slider = dbc.FormGroup(
    [
        dbc.Label("Maximum number of epochs"),
        dcc.Slider(
            id="k-means-max-epoch-slider",
            min=1,
            max=20,
            step=1,
            value=10,
            tooltip={"always_visible": True, "placement": "bottom"},
        ),
        dbc.FormText(
            "Maximum number of iterations of the k-means algorithm for a single run.",
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
        active_tab="dimensionality",
        card=True,
    )
]

clustering_tabs = [
    dbc.Tabs(
        [
            dbc.Tab(tab_id="k-means", label="k-means"),
            dbc.Tab(tab_id="GMM-EM", label="GMM-EM"),
        ],
        id="clustering-tabs",
        card=True,
        active_tab="k-means",
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

clustering_tab_content = [
    html.Div(
        [
            dbc.Form(
                [k_means_k_slider, k_means_n_init_slider, k_means_max_epoch_slider]
            ),
            dbc.Button("Run", color="primary", block=True, id="run-k-means"),
        ]
    ),
    html.Div(
        [
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
        style={"display": "None"},
    ),
    html.Div([html.H5("PCA")], style={"display": "None"}),
]

dimensionality_tab_content = [
    html.Div(
        [
            dbc.Form(
                [
                    umap_metric_dropdown,
                    umap_dimensionality_slider,
                    umap_neighbours_slider,
                ]
            ),
            dbc.Button("Run", color="primary", block=True, id="run-umap"),
        ]
    ),
    html.Div(
        [
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
        style={"display": "None"},
    ),
    html.Div([html.H5("PCA")], style={"display": "None"}),
]

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
                            children=dimensionality_tab_content,
                            id="dimensionality-card-body",
                        ),
                    ]
                ),
            ]
        )
    ],
    "clustering": [
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
                        dbc.CardHeader(clustering_tabs),
                        dbc.CardBody(
                            children=clustering_tab_content,
                            id="dimensionality-card-body",
                        ),
                    ]
                ),
            ]
        )
    ],
}

layout = dbc.Card(
    [
        html.A(
            dbc.CardHeader(html.H5("Analyse", className="ml-1")),
            id="analysis-collapse-toggle",
        ),
        dbc.Collapse(
            dbc.CardBody(
                [
                    html.P(
                        "Warning! Due to current limitations, you will need to manually switch to the 'Embedding' tab in order to run embedding algorithms. Likewise for clustering.",
                        style={"color": "red"},
                    ),
                    dbc.Card(
                        children=[
                            dbc.CardHeader(tabs),
                            dbc.CardBody(
                                children=analysis_tab_content["dimensionality"],
                                id="analysis-card-body",
                            ),
                        ]
                    ),
                ]
            ),
            id=f"collapse-analysis",
        ),
    ]
)


@app.callback(
    Output("analysis-card-body", "children"), [Input("analysis-tabs", "active_tab")]
)
def tab_contents_analysis(tab_id: str):
    """
    Callback to switch tabs based on user interaction in the analysis accordion

    :param tab_id: One of 'dimensionality' or 'clustering'
    :return: The HTML layout to display
    """
    return analysis_tab_content[tab_id]


@app.callback(
    Output("dimensionality-card-body", "children"),
    [Input("dimensionality-tabs", "active_tab")],
)
def tab_contents_dimensionality(tab_id):
    """
    Callback to switch tabs based on user interaction in the dimensionality
    reduction tab of the analysis accordion. Here we make all divs hidden and
    then unhide the one we're interested in. This is done to persist the
    selection of hyper-parameters when switching back and forth between tabs.

    :param tab_id: One of 'UMAP', 't-SNE' or 'PCA'
    :return: The HTML layout to display
    """
    tab_index = {"UMAP": 0, "t-SNE": 1, "PCA": 2}[tab_id]
    new_content = dimensionality_tab_content.copy()
    for i in range(3):
        new_content[i].style = {"display": "None"}
    del new_content[tab_index].style
    return new_content


def tab_contents_clustering(tab_id):
    """
    Callback to switch tabs based on user interaction in the clustering tab
    of the analysis accordion. Here we make all divs hidden and then unhide
    the one we're interested in. This is done to persist the selection of
    hyper-parameters when switching back and forth between tabs.

    :param tab_id: One of 'k-means' or 'GMM-EM'
    :return: The HTML layout to display
    """
    tab_index = {"k-means": 0, "GMM-EM": 1}[tab_id]
    new_content = clustering_tab_content.copy()
    for i in range(3):
        new_content[i].style = {"display": "None"}
    del new_content[tab_index].style
    return new_content
