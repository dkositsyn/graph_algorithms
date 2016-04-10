
import copy
import itertools
import collections


class ArcMarks(collections.Mapping):
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
        vertex_from, vertex_to = key
        return self.get_mark(vertex_from, vertex_to)

    def __setitem__(self, key, value):
        vertex_from, vertex_to = key
        self.set_mark(vertex_from, vertex_to, value)

    def __delitem__(self, key):
        vertex_from, vertex_to = key
        self.del_mark(vertex_from, vertex_to)

    def __iter__(self):
        return iter(self._marks)

    def __len__(self):
        return len(self._marks)


class Graph(object):
    def __init__(self, vertex_count):
        self._arcs = [set() for _ in xrange(vertex_count)]  # doesn't support multiple arcs
        self._reversed_arcs = [set() for _ in xrange(vertex_count)]
        self._marks = ArcMarks()

    @property
    def arc_count(self):
        return sum(map(len, self._arcs))

    def __iter__(self):
        for adjacent_arcs in self._arcs:
            yield adjacent_arcs

    @property
    def vertex_count(self):
        return len(self._arcs)

    def __len__(self):
        return self.vertex_count

    def get_forward(self, vertex_idx):
        return self._arcs[vertex_idx]

    def get_backward(self, vertex_idx):
        return self._reversed_arcs[vertex_idx]

    def __getitem__(self, vertex_idx):
        return self.get_forward(vertex_idx)

    def has(self, vertex_from, vertex_to):
        return vertex_to in self[vertex_from]

    def get_mark_collection(self):
        """:return ArcMarks"""
        return self._marks.copy()

    def get_mark(self, vertex_from, vertex_to):
        return self._marks.get_mark(vertex_from, vertex_to)

    def set_mark(self, vertex_from, vertex_to, value):
        self._marks.set_mark(vertex_from, vertex_to, value)

    def add(self, vertex_from, vertex_to, value=None):
        if vertex_from != vertex_to:  # doesn't support loops
            self._arcs[vertex_from].add(vertex_to)
            self._reversed_arcs[vertex_to].add(vertex_from)
            if value is not None:
                self._marks.set_mark(vertex_from, vertex_to, value)

    def remove(self, vertex_from, vertex_to):
        self._arcs[vertex_from].remove(vertex_to)
        self._reversed_arcs[vertex_to].remove(vertex_from)
        self._marks.del_mark(vertex_from, vertex_to)

    def copy(self):
        """:return Graph"""
        return copy.deepcopy(self)


class UndirectedGraph(Graph):
    @property
    def edge_count(self):
        return self.arc_count

    def __iter__(self):
        for (adj_arcs, adj_backward_arcs) in itertools.izip(self._arcs, self._reversed_arcs):
            yield itertools.chain(adj_arcs, adj_backward_arcs)

    def get_adjacent(self, vertex_idx):
        return itertools.chain(self.get_forward(vertex_idx), self.get_backward(vertex_idx))

    def __getitem__(self, vertex_idx):
        return self.get_adjacent(vertex_idx)
