
import unittest
from itertools import izip
from graph import Graph


def dijkstra(graph, source):
    assert isinstance(graph, Graph)
    assert 0 <= source < len(graph)

    marks = [None] * len(graph)
    discovered = [False] * len(graph)

    marks[source] = 0

    v_from, mark_from = source, 0

    while v_from >= 0:
        discovered[v_from] = True
        for v_to in graph[v_from]:
            new_mark = mark_from + graph.get_mark(v_from, v_to)
            _relax(marks, v_to, new_mark)
        v_from, mark_from = _find_min_undiscovered(marks, discovered)

    assert all(discovered), "Graph has stand-alone vertices"
    return marks


def _find_min_undiscovered(marks, discovered):
    assert len(marks) == len(discovered)
    min_idx, min_mark = -1, None

    for idx, (mark, discovered) in enumerate(izip(marks, discovered)):
        if not discovered and mark is not None:
            if min_mark is None or min_mark > mark:
                min_idx = idx
                min_mark = mark

    return min_idx, min_mark


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

        marks = dijkstra(graph, 0)
        expected_marks = [0, 3, 6, 5, 11, 15]

        self.assertListEqual(marks, expected_marks)


if __name__ == '__main__':
    unittest.main()
