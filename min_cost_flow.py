
import unittest
from copy import deepcopy

from graph import Graph, ArcMarks
from graph_helper import ARC_FLOW_LIMIT

from bellman_ford import bellman_ford


def min_cost_flow(graph, cost_marks, source, target):
    assert isinstance(graph, Graph)
    assert isinstance(cost_marks, ArcMarks)
    assert 0 <= source < len(graph)
    assert 0 <= target < len(graph)

    original_graph = graph
    original_cost_marks = cost_marks

    graph = graph.copy()
    cost_marks = deepcopy(cost_marks)

    # add backward arcs with zero capacity and opposite cost
    for v_from, v_to_collection in enumerate(original_graph):
        for v_to in v_to_collection:
            graph.add(v_to, v_from, 0)

    for (v_from, v_to), cost in original_cost_marks.iteritems():
        cost_marks.set_mark(v_to, v_from, -cost)

    # initialize flow
    flow_marks = graph.get_mark_collection()
    flow_marks.reset_marks(0)  # set zero flow

    rest_flow_graph = graph.copy()  # graph to update weights during iteration

    max_flow, flow_cost = 0, 0
    is_done = False

    while not is_done:
        # create rest flow graph (arcs with weight = (cost - flow))
        for v_from, v_to_collection in enumerate(graph):
            for v_to in v_to_collection:
                max_arc_flow = graph.get_mark(v_from, v_to)
                current_flow = flow_marks[(v_from, v_to)]
                arc_exists = (max_arc_flow != current_flow)

                weight = cost_marks[(v_from, v_to)] if arc_exists else ARC_FLOW_LIMIT
                rest_flow_graph.set_mark(v_from, v_to, weight)

        marks, prev_vertex_marks, last_relaxed_vertices = bellman_ford(rest_flow_graph, source)

        assert not last_relaxed_vertices, "Intermediate graph has cycles with negative weight"

        min_path_length = marks[target]

        if min_path_length < ARC_FLOW_LIMIT:
            # find minimal flow
            extra_flow = ARC_FLOW_LIMIT
            curr_vertex, prev_vertex = target, prev_vertex_marks[target]

            while prev_vertex is not None:
                max_arc_flow = graph.get_mark(prev_vertex, curr_vertex)
                current_flow = flow_marks[(prev_vertex, curr_vertex)]
                possible_extra_flow = max_arc_flow - current_flow
                extra_flow = min(extra_flow, possible_extra_flow)
                curr_vertex, prev_vertex = prev_vertex, prev_vertex_marks[prev_vertex]

            max_flow += extra_flow

            # update current flow and flow cost
            curr_vertex, prev_vertex = target, prev_vertex_marks[target]

            while prev_vertex is not None:
                arc_cost = cost_marks[(prev_vertex, curr_vertex)]
                flow_marks[(prev_vertex, curr_vertex)] += extra_flow
                flow_marks[(curr_vertex, prev_vertex)] -= extra_flow  # for paired arc
                flow_cost += arc_cost * extra_flow
                curr_vertex, prev_vertex = prev_vertex, prev_vertex_marks[prev_vertex]
        else:
            # (min_path_length >= ARC_FLOW_LIMIT) is similar to have no path => optimal result
            is_done = True

    return max_flow, flow_cost, flow_marks


class TestCase(unittest.TestCase):
    def test_simple(self):
        graph = Graph(6)
        cost_marks = graph.get_mark_collection()

        def _add_arc_with_max_flow_and_cost(v_from, v_to, max_flow, cost):
            graph.add(v_from, v_to, max_flow)
            cost_marks[(v_from, v_to)] = cost

        _add_arc_with_max_flow_and_cost(0, 1, 3, 10)
        _add_arc_with_max_flow_and_cost(0, 2, 15, 7)
        _add_arc_with_max_flow_and_cost(1, 2, 7, 12)
        _add_arc_with_max_flow_and_cost(1, 3, 2, 3)
        _add_arc_with_max_flow_and_cost(2, 1, 13, 22)
        _add_arc_with_max_flow_and_cost(2, 4, 5, 16)
        _add_arc_with_max_flow_and_cost(3, 2, 1, 1)
        _add_arc_with_max_flow_and_cost(3, 5, 20, 20)
        _add_arc_with_max_flow_and_cost(4, 3, 3, 14)
        _add_arc_with_max_flow_and_cost(4, 5, 4, 31)

        actual_max_flow, actual_flow_cost, actual_flow_marks = min_cost_flow(graph, cost_marks, 0, 5)
        expected_flow_value = 7
        expected_flow_cost = 339

        self.assertEqual(expected_flow_value, actual_max_flow)
        self.assertEqual(expected_flow_cost, actual_flow_cost)


if __name__ == '__main__':
    unittest.main()
