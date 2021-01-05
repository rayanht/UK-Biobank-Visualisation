import dash
import dash_bootstrap_components as dbc

app = dash.Dash(
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css",
    ]
)

app.config.suppress_callback_exceptions = True
app.config.prevent_initial_callbacks = True
app.title = "UK Biobank Explorer"
