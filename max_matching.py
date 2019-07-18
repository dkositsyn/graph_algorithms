
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


def _iter_matrix_row(matrix, row_idx):
    return iter(matrix[row_idx])


def _iter_matrix_col(matrix, col_idx):
    for row_idx in xrange(len(matrix)):
        yield matrix[row_idx][col_idx]


def max_matching_adjacency_matrix(adjacency_matrix):
    SELECTED = -1
    NO_PREVIOUS = -1
    ARC = 1

    height, width = len(adjacency_matrix), len(adjacency_matrix[0])

    # set initial matching
    for row_idx in xrange(height):
        for col_idx in xrange(width):
            if not adjacency_matrix[row_idx][col_idx]:  # None or 0
                continue

            if SELECTED not in _iter_matrix_col(adjacency_matrix, col_idx):
                adjacency_matrix[row_idx][col_idx] = SELECTED
                break

    optimum_found = False
    row_marks, col_marks = None, None

    while not optimum_found:
        rows_to_process = []
        cols_to_process = []
        row_marks, col_marks = [None] * height, [None] * width

        for row_idx in xrange(height):
            if SELECTED not in _iter_matrix_row(adjacency_matrix, row_idx):
                row_marks[row_idx] = NO_PREVIOUS
                rows_to_process.append(row_idx)

        while rows_to_process:
            # mark cols
            for row_idx in rows_to_process:
                for col_idx in xrange(width):
                    if col_marks[col_idx] is None and ARC == adjacency_matrix[row_idx][col_idx]:
                        col_marks[col_idx] = row_idx  # set mark, found in a row with row_index
                        cols_to_process.append(col_idx)

            rows_to_process = []

            # mark rows
            for col_idx in cols_to_process:
                for row_idx in xrange(height):
                    if row_marks[row_idx] is None and SELECTED == adjacency_matrix[row_idx][col_idx]:
                        row_marks[row_idx] = col_idx  # set mark, found in a col with col_idx
                        rows_to_process.append(row_idx)

                if SELECTED not in _iter_matrix_col(adjacency_matrix, col_idx):
                    # no one cell selected in a marked column => augmenting path found
                    prev_col_idx, prev_row_idx = col_idx, col_marks[col_idx]
                    while prev_col_idx != NO_PREVIOUS:
                        prev_row_idx = col_marks[prev_col_idx]
                        adjacency_matrix[prev_row_idx][prev_col_idx] = SELECTED
                        prev_col_idx = row_marks[prev_row_idx]
                        if prev_col_idx != NO_PREVIOUS:
                            adjacency_matrix[prev_row_idx][prev_col_idx] = ARC  # just an arc
                    break

            cols_to_process = []

        if not rows_to_process and not cols_to_process:
            optimum_found = True

    unmarked_rows_count = row_marks.count(None)
    marked_cols_count = width - col_marks.count(None)
    matching_size = unmarked_rows_count + marked_cols_count

    # find arcs in matching
    arcs_in_matching = []
    for row_idx in xrange(height):
        for col_idx in xrange(width):
            if adjacency_matrix[row_idx][col_idx] == SELECTED:
                arcs_in_matching.append((row_idx, col_idx))

    return matching_size, arcs_in_matching


class TestCase(unittest.TestCase):
    def test_simple(self):
        graph = Graph(10)
        left_part_vertices = [0, 1, 2, 3, 4]
        arc_weight = 1

        graph.add(0, 5, arc_weight)
        graph.add(0, 7, arc_weight)
        graph.add(1, 5, arc_weight)
        graph.add(1, 6, arc_weight)
        graph.add(2, 6, arc_weight)
        graph.add(2, 7, arc_weight)
        graph.add(3, 7, arc_weight)
        graph.add(3, 8, arc_weight)
        graph.add(3, 9, arc_weight)
        graph.add(4, 8, arc_weight)

        value, _ = max_matching(graph, left_part_vertices)
        expected_value = 5

        self.assertEqual(value, expected_value)

    def test_simple_bipartite(self):
        adjacency_matrix = [
            [1, None, 1, None, None],
            [1, 1, None, None, None],
            [None, 1, 1, None, None],
            [None, None, 1, 1, 1],
            [None, None, None, 1, None],
        ]

        value, _ = max_matching_adjacency_matrix(adjacency_matrix)
        expected_value = 5

        self.assertEqual(value, expected_value)

    def test_simple_2(self):
        graph = Graph(10)
        left_part_vertices = [0, 1, 2, 3, 4]
        arc_weight = 1

        graph.add(0, 7, arc_weight)
        graph.add(1, 5, arc_weight)
        graph.add(1, 6, arc_weight)
        graph.add(2, 7, arc_weight)
        graph.add(3, 8, arc_weight)
        graph.add(3, 9, arc_weight)
        graph.add(4, 8, arc_weight)

        value, _ = max_matching(graph, left_part_vertices)
        expected_value = 4

        self.assertEqual(value, expected_value)


if __name__ == '__main__':
    unittest.main()
