
import unittest
from copy import deepcopy

from min_cost_flow import min_cost_flow
from ford_fulkerson import ford_fulkerson
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
    # all_assigned = bool(max_flow == min(len(left_part_vertices), len(right_part_vertices)))

    optimal_assignment_value = graph_helper.get_arcs_with_flow(flow_marks, (new_source_idx, new_target_idx))

    return flow_cost, optimal_assignment_value


def hungarian_algorithm(cost_matrix):
    original_cost_matrix = cost_matrix
    cost_matrix = deepcopy(cost_matrix)
    all_assigned = False
    flow_cost = 0
    optimal_assignment_value = None

    height, width = len(cost_matrix), len(cost_matrix[0])

    # reduce matrix elements (by row)
    min_row_elements = map(min, cost_matrix)
    for row_idx in xrange(height):
        for col_idx in xrange(width):
            cost_matrix[row_idx][col_idx] -= min_row_elements[row_idx]

    # reduce matrix elements (by col)
    min_col_elements = map(min, graph_helper.transpose(cost_matrix))
    for row_idx in xrange(height):
        for col_idx in xrange(width):
            cost_matrix[row_idx][col_idx] -= min_col_elements[col_idx]

    while not all_assigned:
        # transform matrix: set max flow to 1 if matrix element is 0 and None (no arc) otherwise
        max_flow_matrix = [[None] * width for _ in xrange(height)]

        for row_idx in xrange(height):
            for col_idx in xrange(width):
                max_flow_matrix[row_idx][col_idx] = 1 if cost_matrix[row_idx][col_idx] == 0 else None

        graph, left_part_vertices = graph_helper.make_bipartite_graph_from_matrix(max_flow_matrix)

        left_part_vertices = set(left_part_vertices)
        right_part_vertices = set(xrange(len(graph))).difference(left_part_vertices)

        #  add zero cost arcs
        graph, new_source_idx = graph_helper.add_new_source(graph, left_part_vertices, 1)
        graph, new_target_idx = graph_helper.add_new_target(graph, right_part_vertices, 1)

        # find max flow
        max_flow_value, min_cut, flow_marks = ford_fulkerson(graph, new_source_idx, new_target_idx)
        all_assigned = bool(max_flow_value == min(len(left_part_vertices), len(right_part_vertices)))

        if not all_assigned:
            # find minimal cut and marked/unmarked vertices
            min_cut_marked, min_cur_unmarked = min_cut
            left_marked = left_part_vertices.intersection(min_cut_marked)
            left_unmarked = left_part_vertices.intersection(min_cur_unmarked)
            right_marked = right_part_vertices.intersection(min_cut_marked)
            right_unmarked = right_part_vertices.intersection(min_cur_unmarked)

            # find an arc to add - with minimal weight from left_marked to right_unmarked
            min_arc_weight = graph_helper.ARC_COST_LIMIT
            for v_from in left_marked:
                for v_to in right_unmarked:
                    min_arc_weight = min(min_arc_weight, cost_matrix[v_from][v_to - height])

            # decrease arc cost from all left marked vertices and increase it back to all right marked
            # such an action doesn't change cost of arcs between left and right marked (where we have a non-zero flow)
            # but it decrease to zero cost of at least one work, that doesn't correspond to any arc in the graph
            for row_idx in left_marked:
                for col_idx in xrange(width):
                    cost_matrix[row_idx][col_idx] -= min_arc_weight

            for row_idx in xrange(height):
                for col_idx in right_marked:
                    cost_matrix[row_idx][col_idx - height] += min_arc_weight
        else:
            optimal_assignment_value = graph_helper.get_arcs_with_flow(flow_marks, (new_source_idx, new_target_idx))

            for (v_from, v_to) in optimal_assignment_value:
                flow_cost += original_cost_matrix[v_from][v_to - height]

    return flow_cost, optimal_assignment_value


class TestCase(unittest.TestCase):
    def test_optimal_assignment(self):
        # max edge flow is equal to 1 everywhere

        cost_matrix = [
            [7, 5, 6, 3],
            [2, 1, 2, 1],
            [5, 5, 5, 2],
            [4, 4, 5, 2],
        ]

        flow_cost, optimal_assignment_value = optimal_assignment(cost_matrix)

        # optimal assignment is not unique
        # set([(0, 5), (1, 6), (2, 7), (3, 4)]) or [(1, 5), (0, 6), ...]

        self.assertEqual(13, flow_cost)

    def test_hungarian_algorithm(self):
        # max edge flow is equal to 1 everywhere

        cost_matrix = [
            [7, 5, 6, 3],
            [2, 1, 2, 1],
            [5, 5, 5, 2],
            [4, 4, 5, 2],
        ]

        flow_cost, optimal_assignment_value = hungarian_algorithm(cost_matrix)

        # optimal assignment is not unique
        # set([(0, 5), (1, 6), (2, 7), (3, 4)]) or [(1, 5), (0, 6), ...]

        self.assertEqual(13, flow_cost)


if __name__ == '__main__':
    unittest.main()
