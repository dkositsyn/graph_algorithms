
import unittest
from graph import Graph


def floyd_warshall(graph):
    assert isinstance(graph, Graph)
    marks = [[None] * len(graph) for _ in xrange(len(graph))]

    # setup distances
    for v_from in xrange(len(graph)):
        for v_to in xrange(len(graph)):
            if graph.has(v_from, v_to):
                marks[v_from][v_to] = graph.get_mark(v_from, v_to)
        marks[v_from][v_from] = 0  # d(i, i) = 0

    # don't save path currently - only distance
    for last_vertex_idx in xrange(len(graph)):  # |V| - find out negative cycles
        for v_from in xrange(len(graph)):
            for v_to in xrange(len(graph)):
                current_distance = marks[v_from][v_to]
                if marks[v_from][last_vertex_idx] is not None and marks[last_vertex_idx][v_to] is not None:
                    new_distance = marks[v_from][last_vertex_idx] + marks[last_vertex_idx][v_to]
                else:
                    new_distance = None
                if current_distance is None:
                    marks[v_from][v_to] = new_distance
                elif new_distance is not None and current_distance > new_distance:
                    marks[v_from][v_to] = new_distance

    return marks


class TestCase(unittest.TestCase):
    def test_simple(self):
        graph = Graph(6)

        graph.add(0, 1, 3)
        graph.add(0, 2, 15)
        graph.add(1, 2, 7)
        graph.add(1, 3, 2)
        graph.add(2, 4, 5)
        graph.add(3, 2, 1)
        graph.add(3, 5, 20)
        graph.add(4, 3, -3)
        graph.add(4, 5, 4)

        marks = floyd_warshall(graph)
        expected_marks = [[0, 3, 6, 5, 11, 15],
                          [None, 0, 3, 2, 8, 12],
                          [None, None, 0, 2, 5, 9],
                          [None, None, 1, 0, 6, 10],
                          [None, None, -2, -3, 0, 4],
                          [None, None, None, None, None, 0],
                          ]

        for v_from in xrange(len(graph)):
            self.assertListEqual(marks[v_from], expected_marks[v_from])


if __name__ == '__main__':
    unittest.main()
