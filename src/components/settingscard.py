import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import re

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

def update_settings_card(field_id) :
  return dbc.Card(
      [
          dbc.CardBody(
              [
                  html.H4("Settings", className="settings-card-title"),
                  dbc.Label("Graph Type", html_for="settings-graph-type-dropdown"),
                  dcc.Dropdown(
                      id="settings-graph-type-dropdown",
                      options=[
                          {"label": "Violin", "value": 1},
                          {"label": "Scatter", "value": 2},
                          {"label": "Bar", "value": 3},
                      ],
                      value=2,
                      clearable=False
                  )
              ]
          ),
      ],
      style={"minHeight": "40rem"}, # for dummy purposes, to remove later
  )