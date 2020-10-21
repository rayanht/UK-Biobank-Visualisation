import functools
import json
import os
import re
from io import StringIO
from typing import Generator, List, Tuple

import firebase_admin
import jsonpickle
import pandas as pd
from firebase_admin import credentials
from firebase_admin import storage

HIERARCHY_FILENAME = "ukbb_data_field_hierarchy.csv"
META_SUBSET_FILENAME = "ukbb_meta_data_subset.csv"
METADATA_FILENAME = "ukbb_meta_data_21079.csv"


class DatasetLoader:

    def __init__(self):
        self.is_authenticated = False

    def authenticate(self):
        """Authenticate user to firebase"""
        if os.environ.get("ENV") == "PROD":
            cred = credentials.Certificate(json.loads(os.environ.get("GOOGLE_CREDENTIALS")))
        else:
            cred = credentials.Certificate('google-credentials.json')
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'biobank-visualisation.appspot.com'
        })
        self.is_authenticated = True

    def fetch_subset(self, usecols: Tuple = None) -> pd.DataFrame:
        return self.fetch_file(META_SUBSET_FILENAME, usecols)

    def fetch_metadata(self, usecols: Tuple = None, row_limit: int = 500) -> pd.DataFrame:
        return self.fetch_file(METADATA_FILENAME, usecols, row_limit)

    def fetch_hierarchy(self, usecols: Tuple = None) -> pd.DataFrame:
        return self.fetch_file(HIERARCHY_FILENAME, usecols)

    @functools.lru_cache()
    def fetch_file(self, filename: str, usecols: Tuple = None, row_limit: int = None):
        """Retrieve a csv data file and read it, if it hasn't been cached"""
        if os.path.isfile(filename):
            print("Using cached " + filename)
            return pd.read_csv(filename, nrows=row_limit)
        print("Not using cached " + filename)
        if not self.is_authenticated:
            self.authenticate()
        bucket = storage.bucket()
        blob = bucket.blob(filename)

        # TODO: eventually remove this warning/error
        if filename == METADATA_FILENAME:
            if os.environ.get("ENV") == "PROD":
                return self.fetch_file(META_SUBSET_FILENAME, usecols)
            print("PLEASE DOWNLOAD METADATA MANUALLY, dont pull it from database")
            return FileNotFoundError

        if os.environ.get("ENV") != "PROD":
            blob.download_to_filename(META_SUBSET_FILENAME)
        return pd.read_csv(StringIO(blob.download_as_text()), usecols=list(usecols), nrows=row_limit)


class Node:

    def __init__(self, name: str, node_type: str, cat_id=None, field_id=None):
        self.childNodes = dict()
        self.label = name
        self.node_type = node_type
        self.catId = cat_id
        self.fieldId = field_id

    def add_child(self, ids: [int], child) -> None:
        if len(ids) == 1:
            self.childNodes[ids[0]] = child
        else:
            self.childNodes[ids[0]].add_child(ids[1:], child)


def build(raw: pd.DataFrame, prefix="") -> Node:
    """Build tree by adding all intermediate nodes, and only leaf nodes that match the prefix"""
    r = raw.copy(True)
    r["NodeID"] = r["NodeID"].apply(
        lambda node_id: list(filter(lambda s: s != "0", node_id.split("."))))

    root = Node("root", "root")
    prefix_words = prefix.lower().split()
    for row in r.itertuples(index=True, name='Pandas'):
        node_type = row.NodeType
        if node_type == "leaf":
            if prefix == "" \
              or prefix == "Search" \
              or word_prefix(re.sub('[()]', '', row.NodeName.lower()).split(), prefix_words):
                root.add_child(row.NodeID, Node(row.NodeName, "leaf"))
        elif node_type == "sub":
            root.add_child(row.NodeID, Node(row.NodeName, "sub", row.CategoryID, row.FieldID))
        elif node_type == "root":
            root.add_child(row.NodeID, Node(row.NodeName, "root", row.CategoryID, row.FieldID))
    return root


def word_prefix(row: List[str], prefix_words: List[str]) -> bool:
    """Check if string starts with prefix at any point"""
    for i, word in enumerate(row):
        if word.startswith(prefix_words[0]):
            index = 1
            for w in row[i + index:]:
                if index == len(prefix_words):
                    return True
                if not w.startswith(prefix_words[index]):
                    break
                index += 1
            if index == len(prefix_words):
                return True
    return False


def transcode(tree: Node) -> dict:
    """Convert the tree to json"""
    return json.loads(jsonpickle.encode(tree, unpicklable=False))


def gen():
    i = 0
    while True:
        yield i
        i += 1


def flatten(counter: Generator[int, None, None], encoded_tree: dict, clopen_state: dict) -> None:
    """Remove all unnecessary information from the tree after calling build()"""
    encoded_tree["id"] = next(counter)
    if clopen_state.get(str(encoded_tree['id'])):
        encoded_tree["isExpanded"] = clopen_state[str(encoded_tree['id'])]
    else:
        clopen_state[encoded_tree['id']] = False
    if 'childNodes' not in encoded_tree.keys():
        return
    elif encoded_tree['node_type'] == "leaf":
        del encoded_tree['childNodes']
    else:
        encoded_tree['hasCaret'] = True
        encoded_tree['icon'] = 'folder-close'
        encoded_tree['childNodes'] = list(encoded_tree['childNodes'].values())
        for v in encoded_tree['childNodes']:
            flatten(counter, v, clopen_state)


def prune(encoded_tree) -> bool:
    """Remove all nodes that have no children from the tree"""
    if encoded_tree['node_type'] == "leaf":
        return False
    elif encoded_tree['node_type'] == "sub" and len(encoded_tree['childNodes']) == 0:
        return True
    else:
        for child in encoded_tree['childNodes'][:]:
            if prune(child):
                encoded_tree['childNodes'].remove(child)
        if len(encoded_tree['childNodes']) == 0:
            return True


loader = DatasetLoader()


def filter_hierarchy(clopen_state: dict, prefix: str = None) -> (List[dict], dict):
    """Return a tree containing only nodes which have a leaf node with a word starting with the prefix,
    and retains state"""
    counter = gen()
    hierarchy = loader.fetch_hierarchy(usecols=("NodeID", "NodeName", "NodeType", "CategoryID", "FieldID"))
    tree = transcode(build(hierarchy, prefix))
    flatten(counter, tree, clopen_state)
    prune(tree)
    return tree["childNodes"], clopen_state


def get_hierarchy() -> (List[dict], dict):
    """Return a tree with the full hierarchy and no previous state"""
    counter = gen()
    hierarchy = loader.fetch_hierarchy(usecols=("NodeID", "NodeName", "NodeType", "CategoryID", "FieldID"))
    tree = transcode(build(hierarchy))
    clopen_state = {}
    flatten(counter, tree, clopen_state)
    prune(tree)
    return tree["childNodes"], clopen_state


def get_field_names_to_inst():
    fields_info = loader.fetch_hierarchy(usecols=('FieldID', 'NodeName', 'InstanceID', 'RelatedFieldID'))
    field_names_to_inst \
        = fields_info.loc[\
                fields_info['RelatedFieldID'].isnull() \
                & fields_info['FieldID'].notnull()\
            ][['FieldID', 'NodeName', 'InstanceID']]
    return field_names_to_inst


def get_meta_data():
    # return loader.fetch_metadata(row_limit=100).set_index('eid')
    return loader.fetch_subset().set_index('eid')
