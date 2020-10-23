from __future__ import annotations
import functools
import json
import os
import firebase_admin
import pandas as pd
from io import StringIO
from firebase_admin import credentials
from firebase_admin import storage
from src._constants import STORAGE_BUCKET, HIERARCHY_FILENAME
from src.dataset_gateway import Singleton


class HierarchyLoader(metaclass=Singleton):
    def __init__(self):
        self.is_authenticated = False

    def authenticate(self):
        """Authenticate user to firebase"""
        if os.environ.get("ENV") == "PROD":
            cred = credentials.Certificate(
                json.loads(os.environ.get("GOOGLE_CREDENTIALS"))
            )
        else:
            cred = credentials.Certificate("google-credentials.json")
        firebase_admin.initialize_app(cred, {"storageBucket": STORAGE_BUCKET})
        self.is_authenticated = True

    @classmethod
    def fetch_hierarchy(cls) -> pd.DataFrame:
        return cls().fetch_file(HIERARCHY_FILENAME)

    @functools.lru_cache()
    def fetch_file(self, filename: str, row_limit: int = None):
        """Retrieve a csv data file and read it, if it hasn't been cached"""
        if os.path.isfile(filename):
            print("Using cached " + filename)
            return pd.read_csv(filename, nrows=row_limit)
        print("Not using cached " + filename)
        if not self.is_authenticated:
            self.authenticate()
        bucket = storage.bucket()
        blob = bucket.blob(filename)

        if os.environ.get("ENV") != "PROD":
            blob.download_to_filename(filename)
        return pd.read_csv(StringIO(blob.download_as_text()), nrows=row_limit)
