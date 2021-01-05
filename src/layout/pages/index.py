import base64
import os

import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from dash_app import app

with open(os.path.join(os.path.dirname(__file__), "assets", "plot.png"), "rb") as f:
    encoded_image = base64.b64encode(f.read())

card = dbc.Card(
    [
        dbc.CardImg(src=f"data:image/png;base64,{str(encoded_image)[2:-1]}", top=True),
        dbc.CardBody(
            [
                html.H4("Plotting Tool", className="card-title"),
                html.P(
                    "Explore UK Biobank using simple data plots and "
                    "in-browser machine learning algorithms such as dimensionality "
                    "reduction, regression and clustering.",
                    className="card-text",
                ),
                dbc.Button("Go", color="primary", href="/plot"),
            ]
        ),
    ]
)

layout = html.Div(
    [
        html.H2("Welcome to the UK Biobank Explorer"),
        html.H6(
            "Created by: Rayan Hatout / Richard Xiong / Thomas Coste / Lydia He / Archibald Fraikin / Karol Ciszek"
        ),
        html.Br(),
        html.H4("Background"),
        html.P(
            [
                "UK Biobank is a large-scale population study "
                "collecting clinically relevant data from 500,"
                "000 participants, including health, demographics, "
                "lifestyle and genetics. The resulting database is "
                "used to detect early biomarkers of diseases such "
                "as cancer, strokes, diabetes, heart conditions, "
                "arthritis, osteoporosis, eye disorders, "
                "depression and forms of dementia in a middle aged "
                "(40-60 years old) population.",
                html.Br(),
                html.Br(),
                "Unfortunately, the ability to leverage this "
                "dataset for biomedical "
                "research is hindered by the fact that it is not "
                "made "
                "available in a user-friendly format. This "
                "explorer is an early attempt at bridging the gap "
                "between raw data and biomedical insights.",
                html.Br(),
                html.Br(),
                "This project was realised as part of the "
                "third-year "
                "software engineering project at Imperial College "
                "London, under the supervision of ",
                html.A(
                    "Dr. Ben Glocker",
                    href="https://www.imperial.ac.uk/people/b.glocker",
                ),
                " and ",
                html.A(
                    "Stefan Winzeck",
                    href="https://scholar.google.co.uk/citations?user=c3KZ1a0AAAAJ",
                ),
                ".",
                html.Br(),
                html.Br(),
                html.H4("Contributing"),
                "The project is fully open-sourced on ",
                html.A(
                    "GitHub", href="https://github.com/rayanht/UK-Biobank-Visualisation"
                ),
                " and we are accepting feature proposals as well as general suggestions! You'll also be able to find instructions on how to run a local fork in the README.",
            ]
        ),
        dbc.Row([dbc.Col(card, width=6), dbc.Col(card, width=6)]),
    ],
    className="mx-5 my-3",
)
