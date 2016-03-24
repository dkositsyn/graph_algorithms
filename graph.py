
import copy
import collections


class EdgeMarks(collections.Mapping):
    def __init__(self):
        self._marks = {}

    def copy(self):
        return copy.deepcopy(self)

    def get_mark(self, vertex_from, vertex_to):
        return self._marks[(vertex_from, vertex_to)]

    def set_mark(self, vertex_from, vertex_to, value):
        self._marks[(vertex_from, vertex_to)] = value

    def del_mark(self, vertex_from, vertex_to):
        del self._marks[(vertex_from, vertex_to)]

    def reset_marks(self, default_value=None):
        for key in self._marks.iterkeys():
            self._marks[key] = default_value

    def __getitem__(self, key):
        return self._marks[key]

    def __setitem__(self, key, value):
        self._marks[key] = value

    def __iter__(self):
        return iter(self._marks)

    def __len__(self):
        return len(self._marks)


class Graph(object):
    def __init__(self, vertex_count):
        self._arcs = [set() for _ in xrange(vertex_count)]  # doesn't support multiple arcs
        self._marks = EdgeMarks()

    def __iter__(self):
        return iter(self._arcs)

    def __len__(self):
        return len(self._arcs)

    def __getitem__(self, vertex_idx):
        return self._arcs[vertex_idx]

    def has_arc(self, vertex_from, vertex_to):
        return vertex_to in self[vertex_from]

    def get_mark_collection(self):
        """":return EdgeMarks"""
        return self._marks.copy()

    def get_mark(self, vertex_from, vertex_to):
        return self._marks.get_mark(vertex_from, vertex_to)

    def set_mark(self, vertex_from, vertex_to, value):
        self._marks.set_mark(vertex_from, vertex_to, value)

    def add_arc(self, vertex_from, vertex_to, value=None):
        if vertex_from != vertex_to:  # doesn't support loops
            self._arcs[vertex_from].add(vertex_to)
            if value is not None:
                self._marks.set_mark(vertex_from, vertex_to, value)

    def remove_arc(self, vertex_from, vertex_to):
        self._arcs[vertex_from].remove(vertex_to)
        self._marks.del_mark(vertex_from, vertex_to)

    def copy(self):
        return copy.deepcopy(self)

    @staticmethod
    def inverse(graph):
        assert isinstance(graph, Graph)

        new_graph = Graph(len(graph))

        for v_from, v_to_collection in enumerate(graph):
            for v_to in v_to_collection:
                weight = graph.get_mark(v_from, v_to)
                new_graph.add_arc(v_to, v_from, weight)

        return new_graph

    @staticmethod
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

    @staticmethod
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


class UndirectedGraph(object):
    def __init__(self, vertex_count):
        self._graph = Graph(vertex_count)

    def __len__(self):
        return len(self._graph)

    def __getitem__(self, vertex_idx):
        return self._graph[vertex_idx]

    def has_edge(self, vertex_from, vertex_to):
        return vertex_to in self[vertex_from]

    def get_mark(self, v_from, v_to):
        return self._graph.get_mark(v_from, v_to)

    def set_mark(self, v_from, v_to, value):
        return self._graph.set_mark(v_from, v_to, value)

    def add_edge(self, vertex_from, vertex_to, weight=None):
        self._graph.add_arc(vertex_from, vertex_to, weight)
        self._graph.add_arc(vertex_to, vertex_from, weight)

    def remove_edge(self, vertex_from, vertex_to):
        self._graph.remove_arc(vertex_from, vertex_to)
        self._graph.remove_arc(vertex_to, vertex_from)

    def copy(self):
        return copy.deepcopy(self)
