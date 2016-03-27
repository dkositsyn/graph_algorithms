
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

    @property
    def arc_count(self):
        return sum(map(len, self._arcs))

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


class UndirectedGraph(object):
    def __init__(self, vertex_count):
        self._graph = Graph(vertex_count)

    @property
    def edge_count(self):
        return sum(map(len, self._graph)) / 2

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
