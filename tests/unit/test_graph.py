import unittest

import _bootstrap  # noqa: F401

from asf_validator.graph import detect_cycle


class DetectCycleTests(unittest.TestCase):
    def test_no_cycle_in_a_dag(self):
        adjacency = {"a": ["b"], "b": ["c"], "c": []}
        self.assertIsNone(detect_cycle(adjacency))

    def test_direct_cycle(self):
        adjacency = {"a": ["b"], "b": ["a"]}
        cycle = detect_cycle(adjacency)
        self.assertIsNotNone(cycle)
        self.assertEqual(cycle[0], cycle[-1])

    def test_indirect_cycle(self):
        adjacency = {"a": ["b"], "b": ["c"], "c": ["a"]}
        cycle = detect_cycle(adjacency)
        self.assertIsNotNone(cycle)
        self.assertEqual(set(cycle), {"a", "b", "c"})

    def test_edge_to_unknown_node_is_a_leaf_not_a_crash(self):
        adjacency = {"a": ["missing"]}
        self.assertIsNone(detect_cycle(adjacency))

    def test_empty_graph_has_no_cycle(self):
        self.assertIsNone(detect_cycle({}))


if __name__ == "__main__":
    unittest.main()
