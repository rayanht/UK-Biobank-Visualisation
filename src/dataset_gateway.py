from __future__ import annotations

import functools
import hashlib
import json
import os
import time
from io import StringIO
from pathlib import Path
from typing import List, Union

import defusedxml.ElementTree as ETree
import pandas as pd
import requests
from google.cloud import bigquery
from src.dash_app import cache
from src._constants import TABLE_NAME
from src.tree.node import NodeIdentifier


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Query:
    def __init__(self, columns: List[str], limit: int = None, where: str = None):
        self.deferred_min_max = False
        self.df_columns = columns
        self.limit = limit
        self.where = where
        self.query_columns = columns

    def hash(self):
        hash_key = sorted(self.query_columns.copy())
        if self.limit is not None:
            hash_key.append(self.limit)
        hash_key = tuple(hash_key)
        return hashlib.sha224(json.dumps(hash_key).encode("utf-8")).hexdigest()

    def build(self) -> str:
        base_query = f"SELECT {','.join([str(column) for column in self.query_columns])} FROM `{TABLE_NAME}`"
        if self.where:
            base_query += f"WHERE {self.where}"
        if self.limit:
            base_query += f" LIMIT {self.limit}"
        return base_query

    @classmethod
    def from_identifier(cls, node_identifier: NodeIdentifier) -> Query:
        return Query(["eid", node_identifier.db_id()])

    @classmethod
    def from_identifiers(cls, node_identifiers: List[NodeIdentifier]) -> Query:
        return Query(
            ["eid", *[node_identifier.db_id() for node_identifier in node_identifiers]]
        )

    def get_min_max(self):
        if os.environ.get("ENV") == "PROD":
            columns = []
            for id in self.df_columns[1:]:
                columns.append(f"MIN(CAST({id} as NUMERIC))")
                columns.append(f"MAX(CAST({id} as NUMERIC))")
            self.where = []
            for id in self.df_columns[1:]:
                self.where.append(f'{id} != ""')
            self.where = " AND ".join(self.where)
            self.query_columns = columns
        else:
            self.deferred_min_max = True
        self.df_columns = ["min", "max"]
        return self

    def limit_output(self, limit: int):
        self.limit = limit
        return self

    @classmethod
    def all(cls):
        return Query(["*"])


class LocalClient:
    def __init__(self, columns: List[str], aggregate=False):
        self.columns = columns
        self.aggregate = aggregate
        self.df = None

    @classmethod
    def query(cls, _query: Query):
        return LocalClient(_query.query_columns, _query.deferred_min_max)

    def result(self):
        self.df = pd.read_csv(
            Path(os.path.dirname(__file__)).parent.joinpath(
                Path("dataset/ukbb-dataset.csv")
            ),
            usecols=self.columns,
        )

        if self.aggregate:
            self.df = pd.DataFrame(
                [[self.df[self.columns[1]].min(), self.df[self.columns[1]].max()]],
                columns=["min", "max"],
            )
        return self

    def to_dataframe(self) -> pd.DataFrame:
        return self.df


class DatasetGateway(metaclass=Singleton):
    def __init__(self):
        self.client: Union[bigquery.Client, LocalClient]
        if os.environ.get("ENV") == "PROD":
            self.client = bigquery.Client()
        else:
            self.client = LocalClient

    @classmethod
    def submit(cls, _query: Query) -> pd.DataFrame:
        key = _query.hash()
        result = cache.get(key)

        if result is None:
            query = _query
            result_columns = query.df_columns
            if os.environ.get("ENV") == "PROD":
                query = _query.build()
            result: pd.DataFrame
            result = cls().client.query(query).result().to_dataframe()
            result.columns = result_columns
            result_json = result.to_json()
            cache.set(key, result_json)
        else:
            # Skip the function entirely and use the cached value instead.
            result_json = result.decode("utf-8")
            result = pd.read_json(result_json)
        return result


def field_id_meta_data():
    return pd.read_csv(
        os.path.join(os.path.dirname(__file__), "ukbb-public-fields-metadata.csv")
    )


def data_encoding_meta_data(encoding_id):
    """Gets the encoding from the biobank website, and returns it
    in the form of a dict
    """
    r = requests.get(
        f"https://biobank.ctsu.ox.ac.uk/crystal/codown.cgi?id={encoding_id}"
    )

    ENCODING_DATA = StringIO(r.text)

    df = pd.read_csv(ENCODING_DATA, sep="\t", header=0)
    # contains dataframe that may have extra information (including node structure if the
    # encoding is a tree), but this is not needed right now, so we will convert it to a dict

    return df.set_index("coding")["meaning"].to_dict()


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
