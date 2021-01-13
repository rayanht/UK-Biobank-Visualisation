# UK Biobank Visualisation
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/9cc1d9d60e4d409faa259833e7f1af26)](https://www.codacy.com?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=rayanht/UK-Biobank-Visualisation&amp;utm_campaign=Badge_Grade)
[![codecov](https://codecov.io/gh/rayanht/UK-Biobank-Visualisation/branch/main/graph/badge.svg?token=L44KA5MU5N)](https://codecov.io/gh/rayanht/UK-Biobank-Visualisation)

# TL;DR for markers

We are not allowed to distribute the dataset, please head to the live version: https://biobank.hatout.dev/ to play with the app.

------
A web interface to visualise and explore UK Biobank.

![Screenshot of the plotting tool in action](https://storage.googleapis.com/biobank-visualisation.appspot.com/Screenshot%202021-01-07%20at%2017.27.12.png)

## Background
UK Biobank is a large-scale population study collecting clinically relevant data from 500,000 participants, including health, demographics, lifestyle and genetics. The resulting database is used to detect early biomarkers of diseases such as cancer, strokes, diabetes, heart conditions, arthritis, osteoporosis, eye disorders, depression and forms of dementia in a middle aged (40-60 years old) population.

Unfortunately, the ability to leverage this dataset for biomedical research is hindered by the fact that it is not made available in a user-friendly format. This explorer is an early attempt at bridging the gap between raw data and biomedical insights.

This project was realised as part of the third-year software engineering project at [Imperial College London](https://www.imperial.ac.uk/), under the supervision of [Dr. Ben Glocker](https://www.imperial.ac.uk/people/b.glocker) ([@bglocker](https://github.com/bglocker)) and [Stefan Winzeck](https://biomedia.doc.ic.ac.uk/person/stefan-winzeck/).

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

#### Runtimes
The project uses Python >= 3.8.x and Node >= v14.x.x.

[Installing Python](https://realpython.com/installing-python/)

[Installing Node](https://www.freecodecamp.org/news/how-to-install-node-in-your-machines-macos-linux-windows/)

```bash
$ python --version  # 2.7.16 ❌ - beware of the default MacOS installation of Python
$ python3 --version # 3.9.0  ✅
$ node --version # 14.1.0    ✅
```

#### Depedency Management
Depedencies are managed using `pipenv` and `yarn`.

```bash
$ pip/pip3 install --user pipenv
$ pipenv --version # pipenv, version 2020.x.x ✅
```

[Installing yarn](https://classic.yarnpkg.com/en/docs/install/)

```bash
$ yarn --version # 1.22.4 ✅
```

#### Docker (Optional)

### Installing

Follow these instructions to setup a development environment. Skip to the `Deployment` section if you only want to deploy your own version of the explorer.

## Running the tests

### Unit tests

### End to end tests

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dash Plotly](https://plotly.com/dash/) - The web framework used

## Contributing

Please read [CONTRIBUTING.md]() for details on our code of conduct, and the process for submitting pull requests to us.

## Authors

* **Rayan Hatout** - [GitHub](https://github.com/rayanht) | [Twitter](https://twitter.com/rayanhtt) | [LinkedIn](https://www.linkedin.com/in/rayan-hatout/)
* **Richard Xiong** -
* **Thomas Coste** -
* **Archibald Fraikin** -
* **Lydia He** -
* **Karol Ciszek** -

See also the list of [contributors](https://github.com/rayanht/UK-Biobank-Visualisation) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## License Scan

[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Frayanht%2FUK-Biobank-Visualisation.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2Frayanht%2FUK-Biobank-Visualisation?ref=badge_large)
