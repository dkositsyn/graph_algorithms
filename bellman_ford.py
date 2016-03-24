
import unittest
from graph import Graph


def bellman_ford(graph, source):
    assert isinstance(graph, Graph)
    assert 0 <= source < len(graph)

    marks = [None] * len(graph)

    marks[source] = 0

    for iter_idx in xrange(len(graph)):  # |V| - to find out negative cycles
        for v_from in xrange(len(graph)):   # double 'for' - |E|
            mark_from = marks[v_from]

            if mark_from is None:  # nothing to relax
                continue

            for v_to in graph[v_from]:
                new_mark = mark_from + graph.get_mark(v_from, v_to)
                _relax(marks, v_to, new_mark)

    assert all(map(lambda x: isinstance(x, (int, long)), marks)), "Graph has stand-alone vertices"
    return marks


def _relax(marks, v_to, new_mark):
    if marks[v_to] is None or marks[v_to] > new_mark:
        marks[v_to] = new_mark


class TestCase(unittest.TestCase):
    def test_simple(self):
        graph = Graph(6)

        graph.add_arc(0, 1, 3)
        graph.add_arc(0, 2, 15)
        graph.add_arc(1, 2, 7)
        graph.add_arc(1, 3, 2)
        graph.add_arc(2, 4, 5)
        graph.add_arc(3, 2, 1)
        graph.add_arc(3, 5, 20)
        graph.add_arc(4, 3, 3)
        graph.add_arc(4, 5, 4)

        marks = bellman_ford(graph, 0)
        expected_marks = [0, 3, 6, 5, 11, 15]

        self.assertListEqual(marks, expected_marks)


if __name__ == '__main__':
    unittest.main()
