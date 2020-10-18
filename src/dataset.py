import json
import os
from io import StringIO

import firebase_admin
import jsonpickle
import pandas as pd
from firebase_admin import credentials
from firebase_admin import storage

HIERARCHY_FILENAME = "ukbb_data_field_hierarchy.csv"
META_SUBSET_FILENAME = "ukbb_meta_data_subset.csv"

class DatasetLoader:

    def __init__(self):
        self.is_authenticated = False

    def authenticate(self):
        if os.environ.get("ENV") == "PROD":
            cred = credentials.Certificate(json.loads(os.environ.get("GOOGLE_CREDENTIALS")))
        else:
            cred = credentials.Certificate('google-credentials.json')
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'biobank-visualisation.appspot.com'
        })
        self.is_authenticated = True

    def fetch_subset(self, cache=False, usecols=None) -> pd.DataFrame:
        if not self.is_authenticated:
            self.authenticate()
        if os.path.isfile(META_SUBSET_FILENAME):
            print("Using cached meta data subset")
            return pd.read_csv("ukbb_meta_data_subset.csv")
        bucket = storage.bucket()
        blob = bucket.blob("ukbb_meta_data_subset.csv")
        if cache:
            blob.download_to_filename(META_SUBSET_FILENAME)
        return pd.read_csv(StringIO(blob.download_as_text()), usecols=usecols)

    def fetch_hierarchy(self, cache=False, usecols=None) -> pd.DataFrame:
        if not self.is_authenticated:
            self.authenticate()
        if os.path.isfile(HIERARCHY_FILENAME):
            print("Using cached hierarchy")
            return pd.read_csv("ukbb_data_field_hierarchy.csv")
        bucket = storage.bucket()
        blob = bucket.blob("ukbb_data_field_hierarchy.csv")
        if cache:
            blob.download_to_filename(HIERARCHY_FILENAME)
        return pd.read_csv(StringIO(blob.download_as_text()), usecols=usecols)


class Node:

    def __init__(self, name, catId=None, fieldId=None):
        self.childNodes = dict()
        self.label = name
        self.catId = catId
        self.fieldId = fieldId

    def add_child(self, ids, child):
        if len(ids) == 1:
            self.childNodes[ids[0]] = child
        else:
            self.childNodes[ids[0]].add_child(ids[1:], child)


def build(raw) -> Node:
    raw["NodeID"] = raw["NodeID"].apply(
        lambda node_id: list(filter(lambda s: s != "0", node_id.split("."))))

    root = Node("root")
    raw.sort_values(by=['NodeID'])

    for row in raw.itertuples(index=True, name='Pandas'):
        if (row.NodeType != "rel") & (row.NodeType != "inst") : # Only map sub and leaf nodes, but may want to add instance node to each leaf node later on
            root.add_child(row.NodeID, Node(row.NodeName, row.CategoryID, row.FieldID))

    return root


def transcode(tree: Node) -> dict:
    return json.loads(jsonpickle.encode(tree, unpicklable=False))


def gen():
    i = 0
    while True:
        yield i
        i += 1


counter = gen()
datasetloader = DatasetLoader()

def prune_and_flatten(encoded_tree: dict, i=0):
    encoded_tree["id"] = next(counter)
    if 'childNodes' not in encoded_tree.keys():
        return
    elif encoded_tree['childNodes'] == {}:
        del encoded_tree['childNodes']
    else:
        encoded_tree['hasCaret'] = True
        encoded_tree['icon'] = 'folder-close'
        encoded_tree['childNodes'] = list(encoded_tree['childNodes'].values())
        for v in encoded_tree['childNodes']:
            prune_and_flatten(v, i)


def get_hierarchy():
    hierarchy = datasetloader.fetch_hierarchy(cache=True, usecols=["NodeID", "NodeName", "NodeType"])
    tree = transcode(build(hierarchy))
    prune_and_flatten(tree)
    return tree["childNodes"]

def get_field_names_to_inst():
    fields_info = datasetloader.fetch_hierarchy(cache=True, 
                    usecols=['FieldID', 'NodeName', 'InstanceID', 'RelatedFieldID'])
    field_names_to_inst \
        = fields_info.loc[\
                fields_info['RelatedFieldID'].isnull() \
                & fields_info['FieldID'].notnull()\
            ][['FieldID', 'NodeName', 'InstanceID']]
    return field_names_to_inst

def get_meta_data():
    # TODO: change to actual data
    return datasetloader.fetch_subset(cache=True).set_index('eid')