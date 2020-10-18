import json
import os
from io import StringIO
from typing import Generator, List

import firebase_admin
import jsonpickle
import pandas as pd
from firebase_admin import credentials
from firebase_admin import storage

HIERARCHY_FILENAME = "ukbb_data_field_hierarchy.csv"


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

    def fetch_hierarchy(self, cache: bool = False, usecols: [str] = None) -> pd.DataFrame:
        """Retrieve the hierarchy file if it hasn't been cached, then read it"""
        if not self.is_authenticated:
            self.authenticate()
        if os.path.isfile(HIERARCHY_FILENAME):
            print("Using cached hierarchy")
            return pd.read_csv(HIERARCHY_FILENAME, usecols=usecols)
        bucket = storage.bucket()
        blob = bucket.blob(HIERARCHY_FILENAME)
        if cache:
            blob.download_to_filename(HIERARCHY_FILENAME)
        return pd.read_csv(StringIO(blob.download_as_text()), usecols=usecols)


class Node:

    def __init__(self, name: str, node_type: str):
        self.childNodes = dict()
        self.label = name
        self.node_type = node_type

    def add_child(self, ids: [int], child) -> None:
        if len(ids) == 1:
            self.childNodes[ids[0]] = child
        else:
            self.childNodes[ids[0]].add_child(ids[1:], child)


def build(raw: pd.DataFrame, prefix="") -> Node:
    """Build tree by adding all intermediate nodes, and only leaf nodes that match the prefix"""
    raw["NodeID"] = raw["NodeID"].apply(
        lambda node_id: list(filter(lambda s: s != "0", node_id.split("."))))

    root = Node("root", "root")
    for row in raw.itertuples(index=True, name='Pandas'):
        node_type = row.NodeType
        if node_type == "leaf":
            if prefix == "" or word_prefix(row.NodeName.lower(), prefix.lower()):
                root.add_child(row.NodeID, Node(row.NodeName, "leaf"))
        elif node_type == "sub":
            root.add_child(row.NodeID, Node(row.NodeName, "sub"))
        elif node_type == "root":
            root.add_child(row.NodeID, Node(row.NodeName, "root"))
    return root


def word_prefix(row: str, prefix: str) -> bool:
    """Check if a word in the string starts with the prefix"""
    for word in row.split():
        if word.startswith(prefix):
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
    hierarchy = loader.fetch_hierarchy(cache=True, usecols=["NodeID", "NodeName", "NodeType"])
    tree = transcode(build(hierarchy, prefix))
    flatten(counter, tree, clopen_state)
    prune(tree)
    return tree["childNodes"], clopen_state


def get_hierarchy() -> (List[dict], dict):
    """Return a tree with the full hierarchy and no previous state"""
    counter = gen()
    hierarchy = loader.fetch_hierarchy(cache=True, usecols=["NodeID", "NodeName", "NodeType"])
    tree = transcode(build(hierarchy))
    clopen_state = {}
    flatten(counter, tree, clopen_state)
    prune(tree)
    return tree["childNodes"], clopen_state
