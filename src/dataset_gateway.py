from __future__ import annotations

import json
import os
import tempfile
from typing import List

import pandas as pd
from google.cloud import bigquery

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
        with tempfile.NamedTemporaryFile() as tf:
            json.dump(tf, json.loads(os.environ.get("GOOGLE_CREDENTIALS")))
            return bigquery.Client.from_service_account_json(tf.name)
    return bigquery.Client.from_service_account_json("google-credentials.json")


class DatasetGateway(metaclass=Singleton):

    def __init__(self):
        self.client: bigquery.Client
        self.client = authenticate()

    @classmethod
    def submit(cls, _query: Query) -> pd.DataFrame:
        return cls().client.query(_query.build()).result().to_dataframe()
