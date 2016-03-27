
import unittest
from collections import namedtuple

import graph_helper
from graph import Graph


SENTINEL_VERTEX = -1
VertexMark = namedtuple('VertexMark', ['prev', 'is_forward', 'estimate'])


def _dfs(graph, inverse_graph, source, target, marks, edge_marks, discovered):
    extra_flow = None

    if source == target:
        extra_flow = marks[target].estimate

    # forward arcs
    v_from = source
    for v_to in graph[v_from]:
        if extra_flow is None and not discovered[v_to] and marks[v_to].prev is None:
            edge_flow = edge_marks[(v_from, v_to)]
            max_edge_flow = graph.get_mark(v_from, v_to)

            if edge_flow == max_edge_flow:
                continue

            if marks[v_from].estimate is None:
                estimate_to = max_edge_flow - edge_flow
            else:
                estimate_to = min(marks[v_from].estimate, max_edge_flow - edge_flow)

            marks[v_to] = VertexMark(v_from, True, estimate_to)
            extra_flow = _dfs(graph, inverse_graph, v_to, target, marks, edge_marks, discovered)

    # backward arcs
    v_to = source
    for v_from in inverse_graph[v_to]:  # use inverse graph just to know arcs
        if extra_flow is None and not discovered[v_from] and marks[v_from].prev is None:
            edge_flow = edge_marks[(v_from, v_to)]

            if edge_flow == 0:
                continue

            if marks[v_from].estimate is None:
                estimate_from = edge_flow
            else:
                estimate_from = min(marks[v_to].estimate, edge_flow)

            marks[v_from] = VertexMark(v_to, False, estimate_from)
            extra_flow = _dfs(graph, inverse_graph, v_from, target, marks, edge_marks, discovered)

    discovered[source] = True

    return extra_flow


def _update_edge_marks(extra_flow, source, target, marks, edge_marks):
    v_prev = target

    while v_prev != source:
        v_curr, v_prev = v_prev, marks[v_prev].prev
        is_forward = marks[v_curr].is_forward

        if is_forward:
            edge_marks[(v_prev, v_curr)] += extra_flow
        else:
            edge_marks[(v_curr, v_prev)] -= extra_flow


def _estimate_max_flow(graph, source, edge_marks):
    flow = 0

    for v_to in graph[source]:
        flow += edge_marks[(source, v_to)]

    return flow


def _get_min_cut(marks):
    source_vertices, target_vertices = set(), set()

    for vertex_idx, mark in enumerate(marks):
        if mark.prev is not None:
            source_vertices.add(vertex_idx)
        else:
            target_vertices.add(vertex_idx)

    return source_vertices, target_vertices


def _get_cut_arcs(min_cut, edge_marks):
    source_vertices, target_vertices = min_cut

    min_cut_arcs = set()

    for v_from in source_vertices:
        for v_to in target_vertices:
            flow_value = edge_marks.get((v_from, v_to), 0)
            if flow_value:
                min_cut_arcs.add((v_from, v_to))

    return min_cut_arcs


def ford_fulkerson(graph, source, target):
    assert isinstance(graph, Graph)
    assert 0 <= source < len(graph)
    assert 0 <= target < len(graph)

    inverse_graph = graph_helper.inverse(graph)  # just to know backward arcs

    edge_marks = graph.get_mark_collection()
    edge_marks.reset_marks(0)  # set zero flow

    marks = None

    extra_flow = -1  # just to speed up algorithm

    while extra_flow:
        discovered = [False] * len(graph)

        marks = [VertexMark(None, None, None)] * len(graph)
        marks[source] = VertexMark(SENTINEL_VERTEX, None, None)

        extra_flow = _dfs(graph, inverse_graph, source, target, marks, edge_marks, discovered)

        if extra_flow:
            _update_edge_marks(extra_flow, source, target, marks, edge_marks)

    max_flow_value = _estimate_max_flow(graph, source, edge_marks)
    min_cut = _get_min_cut(marks)
    min_cut_arcs = _get_cut_arcs(min_cut, edge_marks)

    return max_flow_value


def ford_fulkerson_multi(graph, sources, targets):
    assert isinstance(graph, Graph)

    graph, new_source = graph_helper.add_new_source(graph, sources)
    graph, new_target = graph_helper.add_new_target(graph, targets)

    max_flow_value = ford_fulkerson(graph, new_source, new_target)
    return max_flow_value


class TestCase(unittest.TestCase):
    def test_simple(self):
        graph = Graph(6)

        graph.add_arc(0, 1, 3)
        graph.add_arc(0, 2, 15)
        graph.add_arc(1, 2, 7)
        graph.add_arc(1, 3, 2)
        graph.add_arc(2, 1, 13)
        graph.add_arc(2, 4, 5)
        graph.add_arc(3, 2, 1)
        graph.add_arc(3, 5, 20)
        graph.add_arc(4, 3, 3)
        graph.add_arc(4, 5, 4)

        value = ford_fulkerson(graph, 0, 5)
        expected_value = 7

        self.assertEqual(value, expected_value)

    def test_simple_multi(self):
        graph = Graph(6)

        graph.add_arc(0, 1, 7)
        graph.add_arc(0, 2, 2)
        graph.add_arc(1, 0, 13)
        graph.add_arc(1, 3, 5)
        graph.add_arc(2, 1, 1)
        graph.add_arc(2, 4, 20)
        graph.add_arc(3, 2, 3)
        graph.add_arc(3, 5, 4)
        graph.add_arc(4, 5, 9)

        value = ford_fulkerson_multi(graph, [0, 1], [4, 5])
        expected_value = 7

        self.assertEqual(value, expected_value)


if __name__ == '__main__':
    unittest.main()
