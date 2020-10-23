import unittest

from src.app import get_option


class NodeUtilsTest(unittest.TestCase):
    def test_update_dropdown_option(self):
        node = {
            "label": "Date E71 first reported (disorders of branched-chain amino-acid metabolism and fatty-acid "
            "metabolism)",
            "node_type": "leaf",
            "field_id": "130800",
            "instance_id": None,
            "id": 235,
            "isSelected": True,
            "secondaryLabel": {
                "key": None,
                "ref": None,
                "props": {"icon": "tick"},
                "_owner": None,
            },
        }
        label = "Date E71 first reported"
        options = get_option(node)
        self.assertEqual(label, options["label"])
        self.assertEqual(node["label"], options["title"])


if __name__ == "__main__":
    unittest.main()
