import os
import sys
from functools import wraps

import dash
import dash_bootstrap_components as dbc
from redis import Redis
import atexit

sys.path.append(os.path.join(os.path.dirname(__file__), "hierarchy_tree"))
app = dash.Dash(
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css",
    ]
)

if not os.environ.get("ENV") == "PROD" and not os.environ.get("ENV") == "LOCALPROD":
    os.environ["ENV"] = "LOCAL"

cache = Redis(
    host=os.environ.get(
        "REDISHOST", "redis" if os.environ.get("ENV") == "LOCALPROD" else "localhost"
    ),
    port=os.environ.get("REDISPORT", 6379),
)

app.config.suppress_callback_exceptions = True
app.config.prevent_initial_callbacks = True
app.title = "UK Biobank Explorer"


def shutdown_redis():
    print("Shutting down redis")
    cache.shutdown(save=True)


atexit.register(shutdown_redis)
