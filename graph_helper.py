
import unittest
import itertools
import collections
from graph import Graph, UndirectedGraph

ARC_FLOW_LIMIT = 0xFFFFFFFF
ARC_COST_LIMIT = 0xFFFFFFFF


def inverse(graph):
    assert isinstance(graph, Graph)

    new_graph = Graph(len(graph))

    for v_from, v_to_collection in enumerate(graph):
        for v_to in v_to_collection:
            weight = graph.get_mark(v_from, v_to)
            new_graph.add(v_to, v_from, weight)

    return new_graph


def transpose(matrix):
    height, width = len(matrix), len(matrix[0])

    transposed = [[None] * height for _ in xrange(width)]

    for row_idx in xrange(height):
        for col_idx in xrange(width):
            transposed[col_idx][row_idx] = matrix[row_idx][col_idx]

    return transposed


def merge_vertices(graph, *vertex_indices):
    """replace some vertices with one merging their arcs

    :param graph: Graph to merge vertices in
    :param vertex_indices: Vertex indices to merge
    """
    assert isinstance(graph, Graph)
    assert isinstance(vertex_indices, collections.Sequence) and len(vertex_indices) > 1

    target_vertex, vertex_to_remove = min(vertex_indices), max(vertex_indices)

    new_graph = type(graph)(len(graph) - 1)

    for v_from in xrange(len(graph)):
        for v_to in graph.get_forward(v_from):
            weight = graph.get_mark(v_from, v_to)

            # check merged vertices
            if v_from in vertex_indices:
                v_from = target_vertex
            if v_to in vertex_indices:
                v_to = target_vertex

            # shift vertex indices
            if v_from > vertex_to_remove:
                v_from -= 1
            if v_to > vertex_to_remove:
                v_to -= 1

            if new_graph.has(v_from, v_to):
                # update arc weight - sum of weights
                new_weight = weight + new_graph.get_mark(v_from, v_to)
                new_graph.set_mark(v_from, v_to, new_weight)
            else:
                new_graph.add(v_from, v_to, weight)

    return new_graph


def split_vertex(graph, vertex_idx, new_weight=None, add_reversed=False):
    """split one vertex into two adding an edge between them

    :param graph: Graph to merge vertices in
    :param vertex_idx: Vertex index to split
    :param new_weight: Weight of new arc (edge)
    :param add_reversed: Add an edge (instead of just arc) between split vertices
    """
    assert isinstance(graph, Graph)
    target_vertex = len(graph)

    new_graph = type(graph)(len(graph) + 1)

    for v_from in xrange(len(graph)):
        for v_to in graph.get_forward(v_from):
            weight = graph.get_mark(v_from, v_to)
            if v_from == vertex_idx:
                v_from = target_vertex
            new_graph.add(v_from, v_to, weight)

    new_graph.add(vertex_idx, target_vertex, new_weight)
    if add_reversed:
        new_graph.add(target_vertex, vertex_idx, new_weight)

    return new_graph


def add_new_vertex(graph):
    """add new stand-alone vertex"""
    assert isinstance(graph, Graph)
    new_graph = Graph(len(graph) + 1)

    for v_from, v_to_collection in enumerate(graph):
        for v_to in v_to_collection:
            weight = graph.get_mark(v_from, v_to)
            new_graph.add(v_from, v_to, weight)

    return new_graph


def add_new_source(graph, sources, arc_weight=ARC_FLOW_LIMIT):
    new_vertex_idx = len(graph)
    expanded_graph = add_new_vertex(graph)

    for old_source_idx in sources:
        expanded_graph.add(new_vertex_idx, old_source_idx, arc_weight)

    return expanded_graph, new_vertex_idx


def add_new_target(graph, targets, arc_weight=ARC_FLOW_LIMIT):
    new_vertex_idx = len(graph)
    expanded_graph = add_new_vertex(graph)

    for old_target_idx in targets:
        expanded_graph.add(old_target_idx, new_vertex_idx, arc_weight)

    return expanded_graph, new_vertex_idx


def make_bipartite_graph_from_matrix(matrix):
    left_part_size = len(matrix)
    right_part_size = len(matrix[0])
    graph_size = left_part_size + right_part_size  # number of rows + columns

    graph = Graph(graph_size)
    left_part_vertices = []

    for left_part_vertex_idx, cost_collection in enumerate(matrix):
        left_part_vertices.append(left_part_vertex_idx)
        for right_part_vertex_idx, weight in itertools.izip(xrange(left_part_size, graph_size), cost_collection):
            if weight is not None:
                graph.add(left_part_vertex_idx, right_part_vertex_idx, weight)

    return graph, left_part_vertices


def get_arcs_with_flow(flow_marks, artificial_vertices=()):
    arcs_with_flow = []

    for (v_from, v_to), mark in flow_marks.iteritems():
        is_artificial_arc = v_from in artificial_vertices or v_to in artificial_vertices
        is_assigned = bool(flow_marks[(v_from, v_to)])
        if not is_artificial_arc and is_assigned:
            arcs_with_flow.append((v_from, v_to))

    return arcs_with_flow


def has_cycle(graph):
    assert isinstance(graph, Graph)

    # visit colors
    WHITE, GRAY, BLACK = range(3)

    visit_color = [WHITE] * len(graph)

    def _dfs(source, destinations):
        visit_result = True

        if visit_color[source] == WHITE:
            visit_color[source] = GRAY
            for destination in destinations:
                visit_result = _dfs(destination, graph.get_forward(destination))
            visit_color[source] = BLACK
        elif visit_color[source] == GRAY:
            visit_result = False  # cycle exists
        else:  # visit color is black - checked earlier
            visit_result = True

        return visit_result

    for v_from, v_to_collection in enumerate(graph):
        if not _dfs(v_from, v_to_collection):
            return True

    return False


class TestCase(unittest.TestCase):
    def test_has_cycle(self):
        graph = Graph(3)

        graph.add(0, 1)
        graph.add(1, 2)
        graph.add(2, 0)

        self.assertTrue(has_cycle(graph))

        graph.remove(2, 0)
        graph.add(0, 2)

        self.assertFalse(has_cycle(graph))


if __name__ == '__main__':
    unittest.main()
