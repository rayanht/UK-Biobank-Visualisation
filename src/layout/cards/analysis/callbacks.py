from dash.dependencies import Input, Output, State
from sklearn.manifold import TSNE
from umap import UMAP

from analysis.view import analysis_tab_content, dimensionality_tab_content
from src.dash_app import app
from src.dataset_gateway import DatasetGateway, Query
from src.layout.cards.settings.callbacks.instance_selection import (
    _get_updated_instances,
)
from src.layout.cards.settings.callbacks.variable_selection import get_dropdown_id
from src.tree.node import NodeIdentifier
import plotly.express as px
import numpy as np
import dash


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


def compute_embedding(dimensions, sample_size, data_fields, estimator):
    """
    Single entry-point for computations for all dimensionality reduction
    algorithms proposed to users.

    :param dimensions: number of spatial dimensions of the output space
    :param sample_size: number of points to consider as part as the embedding
    :param data_fields: data fields to embed
    :param estimator: an object that implements `fit_transform`
    :return: a scatter plot of the embedding
    """
    # The slider uses a logarithmic scale for a better UX, we need to compute
    # the actual sample size that corresponds to the label.
    corrected_sample_size = int(10 ** sample_size)

    # Query and prune data
    selected = [_get_updated_instances(var["value"])[2] for var in data_fields]
    identifiers = list(map(NodeIdentifier, selected))
    features = DatasetGateway.submit(
        Query.from_identifiers(identifiers).limit_output(corrected_sample_size)
    )
    features = features.replace(r"^\s*$", np.nan, regex=True).dropna()
    features = features.drop(features[features.eid == "eid"].index)

    # Generate the projection
    projection = estimator.fit_transform(features.iloc[:, 1:].to_numpy())
    if dimensions == 3:
        fig = px.scatter_3d(projection, x=0, y=1, z=2, size=1)
    else:
        fig = px.scatter(projection, x=0, y=1, render_mode="webgl")
    return fig


@app.callback(
    [
        Output(component_id="embedding-graph", component_property="figure"),
        Output(
            component_id="loading-dimensionality-target", component_property="children"
        ),
    ],
    [
        Input(component_id="run-umap", component_property="n_clicks"),
        Input(component_id="run-tsne", component_property="n_clicks"),
    ],
    [
        State(component_id="umap-metric-dropdown", component_property="value"),
        State(component_id="umap-dimension-slider", component_property="value"),
        State(component_id="umap-neighbours-slider", component_property="value"),
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
def embedding(
    n1,
    n2,
    umap_metric,
    umap_dimensions,
    umap_neighbours,
    tsne_metric,
    tsne_dimensions,
    tsne_perplexity,
    tsne_learning_rate,
    tsne_epochs,
    data_fields,
    sample_size,
):
    """
    Dispatch function for dimensionality reduction algorithms.

    :param n1: not used
    :param n2: not used
    :param umap_metric: distance metric to use for UMAP
    :param umap_dimensions: number of spatial dimensions of the output for UMAP
    :param umap_neighbours: number of neighbours for UMAP

    :param tsne_metric: distance metric to use for t-SNE
    :param tsne_dimensions: number of spatial dimensions of the output for t-SNE
    :param tsne_perplexity: perplexity of the t-SNE
    :param tsne_learning_rate: learning rate of the t-SNE
    :param tsne_epochs: number of iterations for t-SNE

    :param data_fields: data fields to embed
    :param sample_size: number of points to consider as part as the embedding

    :return: a Plotly Figure and a loading placeholder
    """
    ctx = dash.callback_context
    dummy_loading_output = ""
    # If the callback was not triggered by the user, it's a no-op
    if ctx.triggered[0]["value"] is None or not data_fields:
        return dash.no_update, dummy_loading_output
    # Otherwise determine what algorithm is being used and run the computations
    if ctx.triggered[0]["prop_id"] == "run-umap.n_clicks":
        estimator = UMAP(
            n_components=umap_dimensions,
            init="random",
            random_state=42,
            metric=umap_metric,
            n_neighbors=umap_neighbours,
        )
        dimensions = umap_dimensions
    else:
        estimator = TSNE(
            n_components=tsne_dimensions,
            random_state=42,
            metric=tsne_metric,
            perplexity=tsne_perplexity,
            learning_rate=tsne_learning_rate,
            n_iter=tsne_epochs,
        )
        dimensions = umap_dimensions
    return (
        compute_embedding(dimensions, sample_size, data_fields, estimator),
        dummy_loading_output,
    )
