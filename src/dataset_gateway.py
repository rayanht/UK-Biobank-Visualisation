from __future__ import annotations
import json
from io import StringIO
import os
import requests
import defusedxml.ElementTree as ETree
import functools
import pandas as pd
from google.cloud import bigquery
from typing import List
from src._constants import TABLE_NAME
from src.tree.node import NodeIdentifier


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Query:
    def __init__(self, columns: List[str], limit: int = None):
        self.columns = columns
        self.limit = limit

    def build(self):
        base_query = f"SELECT {','.join([str(column) for column in self.columns])} FROM `{TABLE_NAME}`"
        if self.limit:
            base_query += f" LIMIT {self.limit}"
        return base_query

    @classmethod
    def from_identifier(cls, node_identifier: NodeIdentifier) -> Query:
        return Query([node_identifier.db_id()])

    def limit_output(self, limit: int):
        self.limit = limit
        return self

    @classmethod
    def all(cls):
        return Query(["*"])


def authenticate():
    """Authenticate user to GCP"""
    if os.environ.get("ENV") == "PROD":
        with open("google-credentials.json", "w") as fp:
            json.dump(json.loads(os.environ.get("GOOGLE_CREDENTIALS")), fp)
    return bigquery.Client.from_service_account_json("google-credentials.json")


class DatasetGateway(metaclass=Singleton):
    def __init__(self):
        self.client: bigquery.Client
        self.client = authenticate()

    @classmethod
    def submit(cls, _query: Query) -> pd.DataFrame:
        return cls().client.query(_query.build()).result().to_dataframe()


@functools.lru_cache
def field_id_meta_data():
    r = requests.get("https://biobank.ndph.ox.ac.uk/ukb/scdown.cgi?id=1&fmt=xml")

    columns = [
        "field_id",
        "title",
        "value_type",
        "base_type",
        "item_type",
        "strata",
        "instanced",
        "arrayed",
        "sexed",
        "units",
        "main_category",
        "encoding_id",
        "instance_id",
        "instance_min",
        "instance_max",
        "array_min",
        "array_max",
        "notes",
        "debut",
        "version",
        "num_participants",
        "item_count",
    ]

    return parse_xml(r.text, columns)

@functools.lru_cache
def data_encoding_meta_data(encoding_id):
    """Gets the encoding from the biobank website, and returns it
    in the form of a dict
    """
    r = requests.get(f"https://biobank.ctsu.ox.ac.uk/crystal/codown.cgi?id={encoding_id}")

    ENCODING_DATA = StringIO(r.text)

    df = pd.read_csv(ENCODING_DATA, sep="\t", header=0)
    # contains dataframe that may have extra information (including node structure if the
    # encoding is a tree), but this is not needed right now, so we will convert it to a dict

    return df.set_index('coding')['meaning'].to_dict()

def parse_xml(xml_text, df_cols):
    """Parse the input XML file and store the result in a pandas
    DataFrame with the given columns.

    The first element of df_cols is supposed to be the identifier
    variable, which is an attribute of each node element in the
    XML data; other features will be parsed from the text content
    of each sub-element.
    """

    root = ETree.fromstring(xml_text, forbid_entities=False)
    rows = []

    for node in root:
        res = []
        for i, _ in enumerate(df_cols):
            res.append(node.attrib.get(df_cols[i]))
        rows.append({df_cols[i]: res[i] for i, _ in enumerate(df_cols)})

    out_df = pd.DataFrame(rows, columns=df_cols)

    return out_df
