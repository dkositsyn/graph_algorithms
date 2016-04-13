
import unittest

MAX_COST = 0xFFFFFFFF


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
            if cost_matrix[i][j] != MAX_COST and mask & (1 << j):  # index 0 is 0th bit etc.
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


class TestCase(unittest.TestCase):
    def test_simple(self):
        cost_matrix = [[MAX_COST, 5, 2, 4, 5],
                       [3, MAX_COST, 3, 5, 8],
                       [4, 2, MAX_COST, 3, 7],
                       [3, 5, 3, MAX_COST, 2],
                       [1, 4, 2, 5, MAX_COST],
                       ]

        optimal_length, optimal_path = tsp_dynamic(cost_matrix)
        self.assertEquals(12, optimal_length)

        # path is 0 -> 2 -> 1 -> 3 -> 4 --> 0


if __name__ == '__main__':
    unittest.main()
