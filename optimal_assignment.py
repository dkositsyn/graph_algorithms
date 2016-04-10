
import unittest

from min_cost_flow import min_cost_flow
import graph_helper


def optimal_assignment(cost_matrix):
    #  graph has cost mark on its arcs
    graph, left_part_vertices = graph_helper.make_bipartite_graph_from_matrix(cost_matrix)

    left_part_vertices = set(left_part_vertices)
    right_part_vertices = set(xrange(len(graph))) - left_part_vertices

    #  add zero cost arcs
    graph, new_source_idx = graph_helper.add_new_source(graph, left_part_vertices, 0)
    graph, new_target_idx = graph_helper.add_new_target(graph, right_part_vertices, 0)

    cost_marks = graph.get_mark_collection()

    # create max flow marks
    max_flow_marks = graph.get_mark_collection()
    max_flow_marks.reset_marks(1)  # set max flow to 1 on existing arcs

    # change graph marks to max flow instead of cost
    for (v_from, v_to), mark in max_flow_marks.iteritems():
        graph.set_mark(v_from, v_to, mark)

    max_flow, flow_cost, flow_marks = min_cost_flow(graph, cost_marks, new_source_idx, new_target_idx)
    all_assigned = bool(max_flow == min(len(left_part_vertices), len(right_part_vertices)))

    optimal_assignment_value = graph_helper.get_arcs_with_flow(flow_marks, (new_source_idx, new_target_idx))

    return all_assigned, flow_cost, optimal_assignment_value


class TestCase(unittest.TestCase):
    def test_optimal_assignment(self):
        # max edge flow is equal to 1 everywhere

        cost_matrix = [
            [7, 5, 6, 3],
            [2, 1, 2, 1],
            [5, 5, 5, 2],
            [4, 4, 5, 2],
        ]

        all_assigned, flow_cost, optimal_assignment_value = optimal_assignment(cost_matrix)

        # optimal assignment is not unique
        # set([(0, 5), (1, 6), (2, 7), (3, 4)]) or [(1, 5), (0, 6), ...]

        self.assertTrue(all_assigned)
        self.assertEqual(13, flow_cost)


if __name__ == '__main__':
    unittest.main()
