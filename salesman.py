
import unittest
from copy import deepcopy

import heapq
from functools import total_ordering

from graph import Graph
import graph_helper

MAX_COST = 0xFFFFFFFF  # infinity in fact


def tsp_dynamic(cost_matrix):
    _height, _width = len(cost_matrix), len(cost_matrix[0])
    assert _height == _width
    n = _height

    # matrix of min length of path from 0 to i containing masked vertices
    d = [[MAX_COST] * (2 ** n) for _ in xrange(n)]
    d[0][0] = 0

    def _find_optimal_length(i, mask):
        if d[i][mask] != MAX_COST:
            return d[i][mask]

        for j in xrange(n):
            # if arc j->i exists and mask states that vertex "j" is on the current path
            if cost_matrix[j][i] != MAX_COST and mask & (1 << j):  # index 0 is 0th bit etc.
                # try update: check whether d[j][mask-2^j] + cost_matrix[j][i] is less than current minimum
                # note: mask-2^j is mask with j'th bit unset
                d[i][mask] = min(d[i][mask], _find_optimal_length(j, mask & ~(1 << j)) + cost_matrix[j][i])

        return d[i][mask]

    shortest_length = _find_optimal_length(0, 2**n - 1)

    def _find_optimal_path(last_vertex, mask):
        path = [last_vertex]

        while mask:
            i = path[-1]
            for j in xrange(n):
                if d[i][mask] == d[j][mask & ~(1 << j)] + cost_matrix[j][i]:
                    mask &= ~(1 << j)
                    path.append(j)
                    break

        return path

    shortest_path = _find_optimal_path(0, 2**n - 1)

    return shortest_length, shortest_path


@total_ordering
class Vertex(object):
    def __init__(self, matrix, value=0, positions=None):
        assert len(matrix) == len(matrix[0])
        self.matrix = matrix
        self.value = value
        self.positions = positions or []

    def __eq__(self, other):
        assert isinstance(other, Vertex)
        return self.value == other.value

    def __le__(self, other):
        assert isinstance(other, Vertex)
        return self.value < other.value

    def has_cycle(self):
        graph = Graph(self.size)
        for arc in self.positions:
            graph.add(*arc)
        return graph_helper.has_cycle(graph)

    def build_path(self):
        arcs = deepcopy(self.positions)
        vertex_visit_count = [0] * self.size

        for arc in arcs:
            v_from, v_to = arc
            vertex_visit_count[v_from] += 1
            vertex_visit_count[v_to] += 1

        (not_visited, ) = [idx for idx, x in enumerate(vertex_visit_count) if x == 0]
        one_time_visited = [idx for idx, x in enumerate(vertex_visit_count) if x == 1]

        if not self.matrix[not_visited][one_time_visited[0]] and not self.matrix[one_time_visited[1]][not_visited]:
            # path one_time_visited[1] -> not_visited -> one_time_visited[0]
            arcs.append((not_visited, one_time_visited[0]))
            arcs.append((one_time_visited[1], not_visited))
        else:
            # path one_time_visited[0] -> not_visited -> one_time_visited[1]
            arcs.append((not_visited, one_time_visited[1]))
            arcs.append((one_time_visited[0], not_visited))

        arcs = sorted(arcs)
        path = [0]

        for _ in xrange(self.size):
            arc_from_last_vertex = arcs[path[-1]]
            path.append(arc_from_last_vertex[1])

        return path

    def copy(self):
        """:return Vertex"""
        return deepcopy(self)

    @property
    def size(self):
        return len(self.matrix)

    @property
    def actual_size(self):
        return self.size - len(self.positions)

    def _iter_row(self, row_idx):
        return iter(self.matrix[row_idx])

    def _iter_col(self, col_idx):
        return (self.matrix[row_idx][col_idx] for row_idx in xrange(self.size))

    def simplify(self):
        for row_idx in xrange(self.size):
            min_item = min(self._iter_row(row_idx))
            if min_item == 0 or min_item == MAX_COST:
                continue
            for col_idx in xrange(self.size):
                if self.matrix[row_idx][col_idx] != MAX_COST:
                    self.matrix[row_idx][col_idx] -= min_item
            self.value += min_item

        for col_idx in xrange(self.size):
            min_item = min(self._iter_col(col_idx))
            if min_item == 0 or min_item == MAX_COST:
                continue
            for row_idx in xrange(self.size):
                if self.matrix[row_idx][col_idx] != MAX_COST:
                    self.matrix[row_idx][col_idx] -= min_item
            self.value += min_item

        return self.size

    def _find_nonzero_min_row(self, row_idx):
        return min(x for x in self._iter_row(row_idx)
                   if x > 0)

    def _find_nonzero_min_col(self, col_idx):
        return min(x for x in self._iter_col(col_idx)
                   if x > 0)

    def find_zero_with_max_penalty(self):
        max_penalty = -1
        position = None

        nonzero_min_row = [self._find_nonzero_min_row(x) for x in xrange(self.size)]
        nonzero_min_col = [self._find_nonzero_min_col(x) for x in xrange(self.size)]

        for row_idx in xrange(self.size):
            for col_idx in xrange(self.size):
                if self.matrix[row_idx][col_idx] == 0:
                    penalty = nonzero_min_row[row_idx] + nonzero_min_col[col_idx]
                    if penalty > max_penalty:
                        max_penalty = penalty
                        position = (row_idx, col_idx)

        return position

    def get_modified_arc_not_chosen(self, position):
        new_vertex = self.copy()

        x, y = position
        new_vertex.matrix[x][y] = MAX_COST

        return new_vertex

    def get_modified_arc_chosen(self, position):
        new_vertex = self.copy()

        x, y = position

        for idx in xrange(self.size):
            new_vertex.matrix[x][idx] = MAX_COST
            new_vertex.matrix[idx][y] = MAX_COST

        new_vertex.positions.append(position)

        if new_vertex.has_cycle():
            return None

        return new_vertex


def tsp_branch_and_bound(cost_matrix):
    # work correctly for maxtrices with size > 2
    branch_vertices = []
    vertex = Vertex(deepcopy(cost_matrix))
    vertex.simplify()
    heapq.heappush(branch_vertices, vertex)

    best_value, best_vertex = MAX_COST, None

    while True:
        best_estimate = heapq.heappop(branch_vertices)

        if best_estimate.value >= best_value:
            break

        position_of_max_penalized_zero = best_estimate.find_zero_with_max_penalty()

        # cannot have actual size 2:
        # - best estimate hasn't actual size 2 as we don't add right leafs with actual size 2
        # - if best estimate has actual size 3 and there is only 0 (besides infinite values) in a row or column,
        # it'll be chosen as optimal as its penalty will be infinite
        left_leaf = best_estimate.get_modified_arc_not_chosen(position_of_max_penalized_zero)
        left_leaf.simplify()

        heapq.heappush(branch_vertices, left_leaf)

        right_leaf = best_estimate.get_modified_arc_chosen(position_of_max_penalized_zero)

        if right_leaf is None:  # has cycle of length less than size
            continue

        right_leaf.simplify()

        if right_leaf.actual_size == 2:
            if best_value > right_leaf.value:
                best_value = right_leaf.value
                best_vertex = right_leaf
            # else it isn't optimal
        else:
            heapq.heappush(branch_vertices, right_leaf)

    best_path = best_vertex.build_path()

    return best_value, best_path


class TestCase(unittest.TestCase):
    def test_dynamic_programming(self):
        cost_matrix = [[MAX_COST, 5, 2, 4, 5],
                       [3, MAX_COST, 3, 5, 8],
                       [4, 2, MAX_COST, 3, 7],
                       [3, 5, 3, MAX_COST, 2],
                       [1, 4, 2, 5, MAX_COST],
                       ]

        optimal_length, optimal_path = tsp_dynamic(cost_matrix)
        self.assertEquals(12, optimal_length)

        # path is 0 -> 2 -> 1 -> 3 -> 4 --> 0

    def test_branch_and_bound(self):
        cost_matrix = [[MAX_COST, 5, 2, 4, 5],
                       [3, MAX_COST, 3, 5, 8],
                       [4, 2, MAX_COST, 3, 7],
                       [3, 5, 3, MAX_COST, 2],
                       [1, 4, 2, 5, MAX_COST],
                       ]

        optimal_length, optimal_path = tsp_branch_and_bound(cost_matrix)
        self.assertEquals(12, optimal_length)

        # path is 0 -> 2 -> 1 -> 3 -> 4 --> 0


if __name__ == '__main__':
    unittest.main()
