# UK Biobank Visualisation
![Heroku](https://pyheroku-badge.herokuapp.com/?app=biobank-visualisation&style=flat)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/9cc1d9d60e4d409faa259833e7f1af26)](https://www.codacy.com?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=rayanht/UK-Biobank-Visualisation&amp;utm_campaign=Badge_Grade)
[![codecov](https://codecov.io/gh/rayanht/UK-Biobank-Visualisation/branch/main/graph/badge.svg?token=L44KA5MU5N)](https://codecov.io/gh/rayanht/UK-Biobank-Visualisation)

A web interface to visualise and explore the UK Biobank

## Installation (for developers)
The project is managed using Pipenv. To install this, run `pip install --user pipenv`.

Make sure you have Python 3.8 installed, either directly or through the Pyenv version manager. To install the dependencies, run `pipenv install` from project root. You can execute normal Python commands through Pipenv, in the form of `pipenv run python app.py`.

## Local Development

To run the app locally:

`$ gunicorn --pythonpath src/ app:server`

or

`$ cd src/ && gunicorn app:server`