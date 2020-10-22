import unittest
import pandas as pd

from src.tree.node_utils import prune, gen, Node, transcode, build, search_word


class NodeUtilsTest(unittest.TestCase):

    def test_word_search_1(self):
        haystack1 = "Method of measuring blood pressure"
        haystack2 = "Date of birth"
        needle = "Blood"
        self.assertTrue(search_word(needle, haystack1))
        self.assertFalse(search_word(needle, haystack2))

    def test_word_search_2(self):
        haystack1 = "Method of measuring blood pressure"
        haystack2 = "Date of birth"
        needle = "Date of b"
        self.assertTrue(search_word(needle, haystack2))
        self.assertFalse(search_word(needle, haystack1))

    def test_build(self):
        columns = ["NodeID", "NodeType", "NodeName", "FieldID", "InstanceID"]
        node_ids = ["1.0.0.0.0.0.0.0", "2.0.0.0.0.0.0.0", "3.0.0.0.0.0.0.0"]
        node_types = ["root", "root", "root"]
        node_names = ["Population characteristics", "UK Biobank Assessment Centre", "Biological samples"]
        node_field_ids = ["101", "102", "103"]
        node_instance_ids = ["1", "1", "1"]
        frame = pd.DataFrame(list(zip(node_ids, node_types, node_names, node_field_ids, node_instance_ids)),
                             columns=columns)

        tree = transcode(build(frame))
        expected_tree = {'childNodes': {'1': {'childNodes': {},
                                              'label': 'Population characteristics',
                                              'node_type': 'root',
                                              'field_id': "101", 'instance_id': "1"},
                                        '2': {'childNodes': {},
                                              'label': 'UK Biobank Assessment Centre',
                                              'node_type': 'root',
                                              'field_id': "102",
                                              'instance_id': "1"},
                                        '3': {'childNodes': {}, 'label': 'Biological samples', 'node_type': 'root',
                                              'field_id': "103",
                                              'instance_id': "1"}},
                         'label': 'root',
                         'node_type': 'root',
                         'instance_id': None,
                         'field_id': None}

        self.assertEqual(tree, expected_tree)

    def test_transcode(self):
        tree = Node("root", "root")
        expected_transcoded_tree = {'childNodes': {}, 'label': 'root', 'node_type': 'root', 'instance_id': None,
                                    'field_id': None}
        self.assertEqual(transcode(tree), expected_transcoded_tree)

    def test_generator(self):
        counter = gen()
        next(counter)
        self.assertEqual(next(counter), 1)

    def test_prune(self):
        tree = {'childNodes': [{'childNodes': [], 'node_type': 'sub'},
                               {'childNodes': [{'childNodes': [], 'node_type': 'sub'},
                                               {'childNodes': [], 'node_type': 'sub'}],
                                'node_type': 'sub'}],
                'node_type': 'root'}
        expected_tree = {'childNodes': [], 'node_type': 'root'}
        prune(tree)
        self.assertEqual(tree, expected_tree)


if __name__ == '__main__':
    unittest.main()
