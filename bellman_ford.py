
import unittest
from graph import Graph


def bellman_ford(graph, source):
    assert isinstance(graph, Graph)
    assert 0 <= source < len(graph)

    marks = [None] * len(graph)
    prev_vertex_marks = [None] * len(graph)

    marks[source] = 0
    last_relaxed_vertices = None

    for iter_idx in xrange(len(graph)):  # |V| - to find out negative cycles
        last_relaxed_vertices = []  # clear relaxed vertices on the prev. step

        for v_from in xrange(len(graph)):   # double 'for' - |E|
            if marks[v_from] is None:  # nothing to relax
                continue

            for v_to in graph[v_from]:
                _relax(marks, prev_vertex_marks, v_from, v_to, graph.get_mark(v_from, v_to), last_relaxed_vertices)

    # assert all(map(lambda x: isinstance(x, (int, long)), marks)), "Graph has stand-alone vertices"

    # relaxed vertices are vertices on the negative cycle if not empty
    return marks, prev_vertex_marks, last_relaxed_vertices


def _relax(marks, prev_vertex_marks, v_from, v_to, weight, last_relaxed_vertices):
    new_mark = marks[v_from] + weight
    if marks[v_to] is None or marks[v_to] > new_mark:
        marks[v_to] = new_mark
        prev_vertex_marks[v_to] = v_from
        last_relaxed_vertices.append(v_from)


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
        graph.add(4, 3, 3)
        graph.add(4, 5, 4)

        marks, prev_vertex_marks, last_relaxed_vertices = bellman_ford(graph, 0)
        expected_marks = [0, 3, 6, 5, 11, 15]

        self.assertListEqual(marks, expected_marks)

    def test_neg_cycle(self):
        graph = Graph(3)

        graph.add(0, 1, 10)
        graph.add(1, 2, -5)
        graph.add(2, 0, -6)

        marks, prev_vertex_marks, neg_cycle_vertices = bellman_ford(graph, 0)
        expected_neg_cycle_vertices = [0, 1, 2]

        self.assertListEqual(expected_neg_cycle_vertices, neg_cycle_vertices)


if __name__ == '__main__':
    unittest.main()
