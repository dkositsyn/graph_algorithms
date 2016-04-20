
import unittest
import heapq
from graph import Graph, UndirectedGraph


def prim(graph):
    assert isinstance(graph, Graph)

    min_tree_weight = 0
    tree_edges = []
    edges_to_discover = []
    discovered = [False] * len(graph)

    v_from = 0
    discovered[v_from] = True

    # first condition is added to enumerate edges from start vertex as from any other one
    while v_from == 0 or not (all(discovered) or not edges_to_discover):
        # add incident edges that help to discover some vertices
        for v_to in graph[v_from]:
            if not discovered[v_to]:
                edge_weight = graph.get_mark(v_from, v_to)
                # edges will be sorted by weight (then by v_from and v_to) automatically
                heapq.heappush(edges_to_discover, (edge_weight, v_from, v_to))

        # find edge with min. weight from discovered vertex to an undiscovered one
        min_weight, min_v_from, min_v_to = heapq.heappop(edges_to_discover)

        while discovered[min_v_from] and discovered[min_v_to]:
            min_weight, min_v_from, min_v_to = heapq.heappop(edges_to_discover)

        # update
        # only one is discovered
        v_from = min_v_to if discovered[min_v_from] else min_v_from
        discovered[v_from] = True
        tree_edges.append((min_v_from, min_v_to))
        min_tree_weight += min_weight

    assert all(discovered), "Graph has stand-alone vertices"
    return min_tree_weight, tree_edges


class TestCase(unittest.TestCase):
    def test_simple(self):
        graph = UndirectedGraph(5)

        graph.add(0, 1, 7)
        graph.add(0, 2, 3)
        graph.add(0, 3, 2)
        graph.add(0, 4, 6)
        graph.add(1, 2, 9)
        graph.add(1, 3, 4)
        graph.add(1, 4, 8)
        graph.add(2, 3, 4)
        graph.add(2, 4, 5)
        graph.add(3, 4, 5)

        min_tree_weight, tree_edges = prim(graph)
        expected_min_weight = 14

        self.assertEqual(expected_min_weight, min_tree_weight)


if __name__ == '__main__':
    unittest.main()
