
import unittest

import graph_helper
from graph import UndirectedGraph

from prim import prim


def stoer_wagner(graph):
    assert isinstance(graph, UndirectedGraph)

    graph = graph.copy()
    min_cut = graph_helper.ARC_COST_LIMIT  # max possible

    for _ in xrange(len(graph) - 1):
        _, spanning_tree_edges = prim(graph)
        heaviest_edge = spanning_tree_edges[-1]  # it's supposed to be so

        # cut weight is sum of edges adjacent to last joined vertex
        v_last_joined = heaviest_edge[1]
        cut_weight = sum(graph.get_mark(v, v_last_joined) for v in graph.get_adjacent(v_last_joined))

        min_cut = min(min_cut, cut_weight)

        # flip the heaviest edge and merge incident vertices
        graph = graph_helper.merge_vertices(graph, *heaviest_edge)

    return min_cut


class TestCase(unittest.TestCase):
    def test_simple(self):
        graph = UndirectedGraph(4)

        graph.add(0, 1, 10)
        graph.add(0, 2, 4)
        graph.add(1, 2, 5)
        graph.add(1, 3, 6)
        graph.add(2, 3, 5)

        value = stoer_wagner(graph)

        expected_value = 11  # (0, 1, 2) & 3

        self.assertEqual(value, expected_value)
