import json
import re
from typing import Generator, List

import jsonpickle
import pandas as pd

from src.hierarchy import HierarchyLoader
from src.tree.node import Node


def build(raw: pd.DataFrame, counter: Generator[int, None, None], prefix: str = "") -> Node:
    """
    Build tree by adding all intermediate nodes, and only leaf nodes that match the prefix

    :param raw: A raw hierarchy file loaded from its CSV representation
    :param counter: An integer Generator used to uniquely identify the nodes
    :param prefix: optional, used to filter out nodes during search operations
    :return: Node object that encodes the hierarchy
    """
    r = raw.copy(True)
    r["NodeID"] = r["NodeID"].apply(
        lambda node_id: list(filter(lambda s: s != "0", node_id.split(".")))
    )

    root = Node("root", next(counter), "root")
    for row in r.itertuples(index=True, name="Pandas"):
        node_type = row.NodeType
        field_id = str(int(row.FieldID)) if not pd.isnull(row.FieldID) else None
        instance_id = (
            str(int(row.InstanceID)) if not pd.isnull(row.InstanceID) else None
        )
        node = Node(row.NodeName, next(counter), node_type, field_id, instance_id)
        if node_type == "leaf":
            if prefix == "" or prefix == "Search" or search_word(prefix, row.NodeName):
                root.add_child(row.NodeID, node)
        elif node_type == "sub" or node_type == "root":
            root.add_child(row.NodeID, node)
    return root


def search_word(needle: str, haystack: str) -> bool:
    """
    :return: True iff any words in :param description start with :param prefix
    """
    haystack = re.sub("[()]", "", haystack.lower()).split()
    needle = needle.lower().split()
    for i, word in enumerate(haystack):
        if word.startswith(needle[0]):
            index = 1
            for w in haystack[i + index :]:
                if index == len(needle):
                    return True
                if not w.startswith(needle[index]):
                    break
                index += 1
            if index == len(needle):
                return True
    return False


def transcode(tree: Node) -> dict:
    """
    Transcode a Node object into its dictionary representation using a JSON-serialized intermediate.

    :param tree: A Node object as returned by the build function
    :return: The dictionary representation of the Node
    """
    return json.loads(jsonpickle.encode(tree, unpicklable=False))


def gen():
    i = 0
    while True:
        yield i
        i += 1


def flatten(
    encoded_tree: dict, clopen_state: dict
) -> None:
    """
    Transform and enriches an encoded tree into the format expected by the frontend library.

    :param encoded_tree: A tree as returned by the transcode function
    :param clopen_state: A dictionary that keeps track of the open-closed state of a node in the UI
    :return: None, the routine is executed in-place
    """
    if clopen_state.get(str(encoded_tree["id"])):
        if encoded_tree["node_type"] == "leaf":
            encoded_tree["isSelected"] = True
        encoded_tree["isExpanded"] = clopen_state[str(encoded_tree["id"])]
    else:
        clopen_state[str(encoded_tree["id"])] = False
    if "childNodes" not in encoded_tree.keys():
        return
    elif encoded_tree["node_type"] == "leaf":
        del encoded_tree["childNodes"]
    else:
        encoded_tree["hasCaret"] = True
        encoded_tree["icon"] = "folder-close"
        encoded_tree["childNodes"] = list(encoded_tree["childNodes"].values())
        for v in encoded_tree["childNodes"]:
            flatten(v, clopen_state)


def prune(enriched_tree: dict) -> bool:
    """
    Remove all nodes that have no children from the tree

    :param enriched_tree: A tree as returned by the flatten function
    :return: The return value is only used to facilitate the pruning, the operation is executed in-place
    """
    if enriched_tree["node_type"] == "leaf":
        return False
    elif enriched_tree["node_type"] == "sub" and len(enriched_tree["childNodes"]) == 0:
        return True
    else:
        for child in enriched_tree["childNodes"][:]:
            if prune(child):
                enriched_tree["childNodes"].remove(child)
        if len(enriched_tree["childNodes"]) == 0:
            return True


def filter_hierarchy(clopen_state: dict, prefix: str = None) -> (List[dict], dict):
    """
    Return a tree containing only nodes which have a leaf node with a word starting with the prefix,
    and retains state
    """
    counter = gen()
    hierarchy = HierarchyLoader.fetch_hierarchy()
    tree = transcode(build(hierarchy, counter, prefix))
    flatten(tree, clopen_state)
    prune(tree)
    return tree["childNodes"], clopen_state


def get_hierarchy() -> (List[dict], dict):
    """Return a tree with the full hierarchy and a blank state"""
    counter = gen()
    hierarchy = HierarchyLoader.fetch_hierarchy()
    tree = transcode(build(hierarchy, counter))
    clopen_state = {}
    flatten(tree, clopen_state)
    prune(tree)
    return tree["childNodes"], clopen_state


def get_field_names_to_inst():
    fields_info = HierarchyLoader.fetch_hierarchy()
    field_names_to_inst = fields_info.loc[
        fields_info["RelatedFieldID"].isnull() & fields_info["FieldID"].notnull()
    ][["FieldID", "NodeName", "InstanceID"]]
    return field_names_to_inst
