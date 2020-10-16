from csv import reader
# Only for env variables
import os

COLUMNS = [
    "LVL1",
    "LVL2",
    "LVL3",
    "LVL4",
    "LVL5",
    "LVL6",
    "NodeID",
    "NodeType",
    "CategroyID",
    "FieldID",
    "InstanceID",
    "RelatedFieldID",
    "NodeName"
]

def _load_metadata(filename):
    with open(filename) as f:
        md_reader = reader(f)
        return [row for row in md_reader]


class Searcher:
    metadata = None

    # The search is currently very simple and looks for an exact match
    def search(self, token):
        if not token:
            return []

        if not self.metadata:
            self.metadata = _load_metadata(os.environ['METADATA_PATH'])

        name = lambda row: row[COLUMNS.index("NodeName")]
        # Match function is case-insensitive, but the .lower() method is not foolproof
        match = lambda row: token.lower() in name(row).lower()
        return [name(row) for row in self.metadata if match(row)] 

def match(node, string):
    if not node:
        return None

    # Comparison is case-insensitive, but the .lower() method is not foolproof
    try:
        if string.lower() in node["label"].lower():
            return node
        elif not node["childNodes"]:
            return None
    except KeyError:
        return None

    modified = node.copy()
    # print("Visiting node {}, looking for {}".format(node["label"], string))
    modified["childNodes"] = _search(modified["childNodes"], string)
    return modified

# Placeholder function for basic recursive search over the tree
def _search(nodes, string=""):
    if not string:
        return nodes

    if not nodes:
        return []

    return list(filter(None, [match(node, string) for node in nodes]))

def search(nodes, string=""):
    return _search(nodes, string)

if __name__=="__main__":
    results = search("diabetes")
    print(results)
