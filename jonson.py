
import unittest

from graph import Graph
import graph_helper

from bellman_ford import bellman_ford
from dijkstra import dijkstra


def jonson(graph):
    assert isinstance(graph, Graph)

    graph = graph.copy()
    marks = []

    potentials, has_negative_cycle = _compute_potentials(graph)
    assert not has_negative_cycle, "Graph has cycle with negative weight"

    _modify_arcs(graph, potentials)  # now graph hasn't negative weights

    for v_from in xrange(len(graph)):
        v_marks, _ = dijkstra(graph, v_from)

        # return weights back
        v_marks = [v_mark + potentials[v_from] - potentials[v_to] if v_mark is not None else v_mark
                   for v_to, v_mark in enumerate(v_marks)]

        marks.append(v_marks)

    return marks


def _compute_potentials(graph):
    assert isinstance(graph, Graph)

    # add new source with arcs to all vertices
    graph, new_source = graph_helper.add_new_source(graph, range(len(graph)), 0)

    # now distance can be 0 or less than 0
    marks, _, last_relaxed_vertices = bellman_ford(graph, new_source)
    marks = marks[:new_source] + marks[new_source + 1:]  # exclude distance to added source

    potentials = [-x for x in marks]  # potential is a negative distance

    has_negative_cycle = bool(last_relaxed_vertices)

    return potentials, has_negative_cycle


def _modify_arcs(graph, potentials):
    assert isinstance(graph, Graph)
    assert len(graph) == len(potentials)

    for v_from in xrange(len(graph)):
        for v_to in graph.get_forward(v_from):
            weight = graph.get_mark(v_from, v_to)
            new_weight = weight - potentials[v_from] + potentials[v_to]
            graph.set_mark(v_from, v_to, new_weight)

    return graph


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

        marks = jonson(graph)
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
