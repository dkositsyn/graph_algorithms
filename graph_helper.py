
import collections
from graph import Graph

ARC_FLOW_LIMIT = 0xFFFFFFFF


def inverse(graph):
    assert isinstance(graph, Graph)

    new_graph = Graph(len(graph))

    for v_from, v_to_collection in enumerate(graph):
        for v_to in v_to_collection:
            weight = graph.get_mark(v_from, v_to)
            new_graph.add_arc(v_to, v_from, weight)

    return new_graph


def merge_vertices(graph, *vertex_indices):
    """replace some vertices with one merging their arcs

    :param graph: Graph to merge vertices in
    :param vertex_indices: Vertex indices to merge
    """
    assert isinstance(graph, Graph)
    assert isinstance(vertex_indices, collections.Sequence) and len(vertex_indices) > 1
    target_vertex = vertex_indices[0]

    new_graph = Graph(len(graph))

    for v_from, v_to_collection in enumerate(graph):
        for v_to in v_to_collection:
            weight = graph.get_mark(v_from, v_to)
            if v_from in vertex_indices:
                v_from = target_vertex
            if v_to in vertex_indices:
                v_to = target_vertex
            new_graph.add_arc(v_from, v_to, weight)

    return new_graph


def split_vertex(graph, vertex_idx, new_weight=None, add_reversed=False):
    """split one vertex into two adding an edge between them

    :param graph: Graph to merge vertices in
    :param vertex_idx: Vertex index to split
    :param new_weight: Weight of new arc (edge)
    :param add_reversed: Add an edge (instead of just arc) between split vertices
    """
    assert isinstance(graph, Graph)

    new_graph = Graph(len(graph))

    target_vertex = len(graph)

    for v_from, v_to_collection in enumerate(graph):
        for v_to in v_to_collection:
            weight = graph.get_mark(v_from, v_to)
            if v_from == vertex_idx:
                v_from = target_vertex
            new_graph.add_arc(v_from, v_to, weight)

    new_graph.add_arc(vertex_idx, target_vertex, new_weight)
    if add_reversed:
        new_graph.add_arc(target_vertex, vertex_idx, new_weight)

    return new_graph


def add_new_vertex(graph):
    """add new stand-alone vertex"""
    assert isinstance(graph, Graph)
    new_graph = Graph(len(graph) + 1)

    for v_from, v_to_collection in enumerate(graph):
        for v_to in v_to_collection:
            weight = graph.get_mark(v_from, v_to)
            new_graph.add_arc(v_from, v_to, weight)

    return new_graph


def add_new_source(graph, sources, arc_weight=ARC_FLOW_LIMIT):
    new_vertex_idx = len(graph)
    expanded_graph = add_new_vertex(graph)

    for old_source_idx in sources:
        expanded_graph.add_arc(new_vertex_idx, old_source_idx, arc_weight)

    return expanded_graph, new_vertex_idx


def add_new_target(graph, targets, arc_weight=ARC_FLOW_LIMIT):
    new_vertex_idx = len(graph)
    expanded_graph = add_new_vertex(graph)

    for old_target_idx in targets:
        expanded_graph.add_arc(old_target_idx, new_vertex_idx, arc_weight)

    return expanded_graph, new_vertex_idx
