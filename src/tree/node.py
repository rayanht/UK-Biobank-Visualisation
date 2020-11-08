from __future__ import annotations

import re
from typing import List


class NodeIdentifier:
    def __init__(self, raw_id):
        self.raw_id = str(raw_id)
        split_id = re.split("[-.]", str(raw_id))
        if len(split_id) >= 1:
            self.field_id = split_id[0]
            self.instance_id, self.part_id = 0, 0
        if len(split_id) >= 2:
            self.instance_id = split_id[1]
            self.part_id = 0
        if len(split_id) == 3:
            self.part_id = split_id[2]

    def db_id(self):
        return f"_{self.field_id}_{self.instance_id}_{self.part_id}"

    def meta_id(self):
        return f"{self.field_id}-{self.instance_id}.{self.part_id}"


class Node:
    def __init__(
        self, name: str, node_id: int, node_type: str, field_id: str = None, instance_id: str = None
    ):
        self.childNodes = dict()
        self.label = name
        self.id = node_id
        self.node_type = node_type
        self.field_id = field_id
        self.instance_id = instance_id

    def add_child(self, ids: List[int], child: Node) -> None:
        if len(ids) == 1:
            self.childNodes[ids[0]] = child
        else:
            self.childNodes[ids[0]].add_child(ids[1:], child)
