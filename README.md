# UK Biobank Visualisation
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/9cc1d9d60e4d409faa259833e7f1af26)](https://www.codacy.com?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=rayanht/UK-Biobank-Visualisation&amp;utm_campaign=Badge_Grade)
[![codecov](https://codecov.io/gh/rayanht/UK-Biobank-Visualisation/branch/main/graph/badge.svg?token=L44KA5MU5N)](https://codecov.io/gh/rayanht/UK-Biobank-Visualisation)

A web interface to visualise and explore UK Biobank

## Installation (for developers)
The project is managed using Pipenv. To install this, run `pip install --user pipenv`.

Make sure you have Python 3.8 installed, either directly or through the Pyenv version manager. To install the dependencies, run `pipenv install` from project root. You can execute normal Python commands through Pipenv, in the form of `pipenv run python app.py`.

This project uses pre-commit, in order to install the hooks locally, run `$ pre-commit install`.

In order to generate necessary Dash components, ensure that you are in the Python virtual environment (i.e. `$ pipenv shell`). Then run `$ sh build_custom_components.sh` in the root directory.

## Local Development

To run the app locally:

`$ gunicorn --pythonpath src/ app:server`

or

`$ cd src/ && gunicorn app:server`

[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Frayanht%2FUK-Biobank-Visualisation.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2Frayanht%2FUK-Biobank-Visualisation?ref=badge_large)
