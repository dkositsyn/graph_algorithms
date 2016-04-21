
import unittest
from graph import ArcMarks, Graph


def min_time(graph):
    # graph numbering is supposed to be correct
    assert isinstance(graph, Graph)

    # source is 0, target is len(graph) - 1
    marks = [0] * len(graph)

    for current_vertex in xrange(1, len(graph)):
        for prev_vertex in graph.get_backward(current_vertex):
            # try update
            marks[current_vertex] = max(marks[current_vertex],
                                        marks[prev_vertex] + graph.get_mark(prev_vertex, current_vertex))

    project_critical_time = marks[-1]
    return project_critical_time, marks


def max_time(graph, project_critical_time):
    # graph numbering is supposed to be correct
    assert isinstance(graph, Graph)

    # source is 0, target is len(graph) - 1
    marks = [0] * len(graph)

    for current_vertex in xrange(len(graph) - 2, 0, -1):
        for next_vertex in graph.get_forward(current_vertex):
            # try update
            marks[current_vertex] = max(marks[current_vertex],
                                        marks[next_vertex] + graph.get_mark(current_vertex, next_vertex))

    for idx, mark in enumerate(marks):
        marks[idx] = project_critical_time - mark

    return marks


def get_reserve_time(graph, min_time_values, max_time_values, eliminate_artificial_arcs=True):
    # graph numbering is supposed to be correct
    assert isinstance(graph, Graph)

    free_reserve_marks = ArcMarks()
    full_reserve_marks = ArcMarks()

    for v_from, v_to_collection in enumerate(graph):
        for v_to in v_to_collection:
            arc_mark = graph.get_mark(v_from, v_to)

            if eliminate_artificial_arcs and not arc_mark:
                continue

            free_reserve_mark = min_time_values[v_to] - min_time_values[v_from] - arc_mark
            free_reserve_marks.set_mark(v_from, v_to, free_reserve_mark)

            full_reserve_mark = max_time_values[v_to] - min_time_values[v_from] - arc_mark
            full_reserve_marks.set_mark(v_from, v_to, full_reserve_mark)

    return free_reserve_marks, full_reserve_marks


class TestCase(unittest.TestCase):
    def test_simple(self):
        graph = Graph(6)

        graph.add(0, 1, 2)
        graph.add(0, 2, 4)
        graph.add(0, 3, 5)
        graph.add(1, 3, 4)
        graph.add(1, 4, 3)
        graph.add(2, 5, 7)
        graph.add(3, 4, 6)
        graph.add(3, 5, 4)
        graph.add(4, 5, 2)

        critical_time, min_time_marks = min_time(graph)
        max_time_marks = max_time(graph, critical_time)
        free_reserve_marks, full_reserve_marks = get_reserve_time(graph, min_time_marks, max_time_marks)

        expected_critical_time = 14
        expected_free_reserve_marks = {
            (0, 1): 0,
            (0, 2): 0,
            (0, 3): 1,
            (1, 3): 0,
            (1, 4): 7,
            (2, 5): 3,
            (3, 4): 0,
            (3, 5): 4,
            (4, 5): 0,
        }
        expected_full_reserve_marks = {
            (0, 1): 0,
            (0, 2): 3,
            (0, 3): 1,
            (1, 3): 0,
            (1, 4): 7,
            (2, 5): 3,
            (3, 4): 0,
            (3, 5): 4,
            (4, 5): 0,
        }

        self.assertEqual(expected_critical_time, critical_time)
        self.assertDictEqual(expected_free_reserve_marks, dict(free_reserve_marks))
        self.assertDictEqual(expected_full_reserve_marks, dict(full_reserve_marks))


if __name__ == '__main__':
    unittest.main()
