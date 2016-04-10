
from copy import deepcopy
import unittest

from max_matching import max_matching
import graph_helper


def optimal_assignment_with_max_element(cost_matrix):
    cost_matrix = deepcopy(cost_matrix)

    min_assignment_element, assignment_cost, optimal_assignment_value = None, None, None

    graph, left_part_vertices = graph_helper.make_bipartite_graph_from_matrix(cost_matrix)
    left_part_size = len(left_part_vertices)

    while True:
        matching_size, new_optimal_assignment_value = max_matching(graph, left_part_vertices)

        all_assigned = bool(matching_size == left_part_size)
        if not all_assigned:
            break

        optimal_assignment_value = new_optimal_assignment_value

        assignment_values = [cost_matrix[v_from][v_to - left_part_size]
                             for (v_from, v_to) in optimal_assignment_value]
        min_assignment_element = min(assignment_values)
        assignment_cost = sum(assignment_values)

        # eliminate arcs with cost less or equal to minimal in the assignment
        for row_idx, row in enumerate(cost_matrix):
            for col_idx, value in enumerate(row):
                if value is not None and value <= min_assignment_element:
                    row[col_idx] = None
                    graph.remove(row_idx, left_part_size + col_idx)

    return min_assignment_element, assignment_cost, optimal_assignment_value


class TestCase(unittest.TestCase):
    def test_optimal_assignment_with_max_element(self):
        cost_matrix = [
            [1, 3, 2, 6, 0, 1],
            [4, 2, 3, 8, 3, 1],
            [8, 1, 1, 5, 0, 9],
            [3, 4, 4, 8, 8, 3],
            [2, 9, 9, 5, 2, 9],
            [3, 3, 3, 6, 7, 1],
        ]

        min_assignment_element, assignment_cost, assignment_value = optimal_assignment_with_max_element(cost_matrix)

        self.assertEqual(min_assignment_element, 4)
        self.assertEqual(assignment_cost, 39)  # but assignment is not unique


if __name__ == '__main__':
    unittest.main()
