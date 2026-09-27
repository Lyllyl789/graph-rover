import unittest

from graph_steps import Graph, bfs, dfs, dijkstra


def sample_graph():
    graph = Graph(directed=True)
    for source, target, weight in (
        ("A", "B", 2), ("A", "C", 5), ("B", "C", 1),
        ("B", "D", 4), ("C", "D", 1),
    ):
        graph.add_edge(source, target, weight)
    graph.add_node("isolated")
    return graph


class GraphTests(unittest.TestCase):
    def test_undirected_edge_and_node_order(self):
        graph = Graph()
        graph.add_edge("B", "A", 2)
        self.assertEqual(graph.nodes, ("B", "A"))
        self.assertEqual(graph.neighbors("A"), (("B", 2.0),))

    def test_invalid_weight(self):
        for weight in (float("nan"), float("inf"), True):
            with self.subTest(weight=weight), self.assertRaises(ValueError):
                Graph().add_edge("A", "B", weight)


class AlgorithmTests(unittest.TestCase):
    def test_bfs_order_and_hops(self):
        run = bfs(sample_graph(), "A")
        self.assertEqual(run.order, ("A", "B", "C", "D"))
        self.assertEqual(run.distances["D"], 2)
        self.assertEqual(run.predecessor["D"], "B")
        self.assertNotIn("isolated", run.distances)

    def test_dfs_order_and_parent(self):
        run = dfs(sample_graph(), "A")
        self.assertEqual(run.order, ("A", "B", "C", "D"))
        self.assertEqual(run.predecessor["D"], "C")

    def test_dijkstra_shortest_path(self):
        run = dijkstra(sample_graph(), "A")
        self.assertEqual(run.distances["D"], 4)
        self.assertEqual(run.predecessor["D"], "C")
        self.assertEqual(run.order, ("A", "B", "C", "D"))

    def test_dijkstra_rejects_negative_even_when_unreachable(self):
        graph = sample_graph()
        graph.add_edge("isolated", "X", -1)
        with self.assertRaisesRegex(ValueError, "nonnegative"):
            dijkstra(graph, "A")

    def test_unknown_start(self):
        for algorithm in (bfs, dfs, dijkstra):
            with self.subTest(algorithm=algorithm.__name__), self.assertRaises(ValueError):
                algorithm(sample_graph(), "missing")

    def test_events_are_sequential_snapshots(self):
        for algorithm in (bfs, dfs, dijkstra):
            with self.subTest(algorithm=algorithm.__name__):
                run = algorithm(sample_graph(), "A")
                self.assertEqual(run.events[0].kind, "start")
                self.assertEqual(run.events[-1].kind, "finish")
                self.assertEqual([event.sequence for event in run.events],
                                 list(range(len(run.events))))
                self.assertEqual(run.events[0].visited, ())
                self.assertEqual(run.events[-1].visited, run.order)
                self.assertEqual(run.events[-1].distances, run.distances)


if __name__ == "__main__":
    unittest.main()
