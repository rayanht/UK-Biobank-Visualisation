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

# The search is currently very simple and looks for an exact match
def search(token):
    metadata = _load_metadata(os.environ['METADATA_PATH'])

    # Match function is case-insensitive, but the .lower() method is not foolproof
    match = lambda row: token.lower() in row[COLUMNS.index("NodeName")].lower()
    return [row for row in metadata if match(row)] 

if __name__=="__main__":
    results = search("diabetes")
    print(results)
