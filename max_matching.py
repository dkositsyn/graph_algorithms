
import unittest
from graph import Graph

from ford_fulkerson import ford_fulkerson
from graph_helper import add_new_source, add_new_target, get_arcs_with_flow


def max_matching(graph, left_part_vertices):
    assert isinstance(graph, Graph)

    left_part_vertices = set(left_part_vertices)
    right_part_vertices = set(xrange(len(graph))) - left_part_vertices

    graph, new_source_idx = add_new_source(graph, left_part_vertices, 1)
    graph, new_target_idx = add_new_target(graph, right_part_vertices, 1)

    max_matching_value, min_cut, flow_marks = ford_fulkerson(graph, new_source_idx, new_target_idx)
    arcs_in_matching = get_arcs_with_flow(flow_marks, (new_source_idx, new_target_idx))

    return max_matching_value, arcs_in_matching


class TestCase(unittest.TestCase):
    def test_simple(self):
        graph = Graph(10)
        left_part_vertices = [0, 1, 2, 3, 4]
        arc_weight = 1

        graph.add(0, 5, arc_weight)
        graph.add(0, 7, arc_weight)
        graph.add(1, 5, arc_weight)
        graph.add(2, 6, arc_weight)
        graph.add(2, 7, arc_weight)
        graph.add(3, 7, arc_weight)
        graph.add(3, 9, arc_weight)
        graph.add(4, 8, arc_weight)

        graph.add(6, 1, arc_weight)
        graph.add(8, 3, arc_weight)

        value, _ = max_matching(graph, left_part_vertices)
        expected_value = 5

        self.assertEqual(value, expected_value)


if __name__ == '__main__':
    unittest.main()
