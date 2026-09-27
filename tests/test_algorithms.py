import unittest

from graph_steps import Graph, Playback, bfs, dfs, dijkstra, parse_graph


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
        for weight in (float("nan"), float("inf"), True, 10**1000):
            with self.subTest(weight=weight), self.assertRaises(ValueError):
                Graph().add_edge("A", "B", weight)


class AlgorithmTests(unittest.TestCase):
    def test_empty_graph_and_isolated_start(self):
        for algorithm in (bfs, dfs, dijkstra):
            with self.subTest(algorithm=algorithm.__name__):
                with self.assertRaisesRegex(ValueError, "unknown node"):
                    algorithm(Graph(), "A")
                graph = Graph()
                graph.add_node("A")
                run = algorithm(graph, "A")
                self.assertEqual(run.order, ("A",))
                self.assertEqual(run.events[-1].kind, "finish")

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

    def test_dijkstra_rejects_distance_overflow(self):
        graph = Graph(directed=True)
        graph.add_edge("A", "B", 1e308)
        graph.add_edge("B", "C", 1e308)
        with self.assertRaisesRegex(ValueError, "finite numeric range"):
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


class UiFoundationTests(unittest.TestCase):
    def test_edge_list_parser_direction_and_default_weight(self):
        directed = parse_graph("A B 2\nB C # default weight", directed=True)
        self.assertEqual(directed.neighbors("A"), (("B", 2.0),))
        self.assertEqual(directed.neighbors("B"), (("C", 1.0),))
        self.assertEqual(directed.neighbors("C"), ())
        undirected = parse_graph("A B", directed=False)
        self.assertEqual(undirected.neighbors("B"), (("A", 1.0),))

    def test_parser_reports_bad_line_and_empty_graph(self):
        with self.assertRaisesRegex(ValueError, "line 2"):
            parse_graph("A B\nC D nope")
        with self.assertRaisesRegex(ValueError, "at least one edge"):
            parse_graph("# only a comment")
        for text in ("A B nan", "A B inf", "A B 1e999", "A B 1 2"):
            with self.subTest(text=text), self.assertRaisesRegex(ValueError, "line 1"):
                parse_graph(text)

    def test_playback_steps_pauses_by_not_advancing_and_resets(self):
        playback = Playback(bfs(sample_graph(), "A"))
        self.assertIsNone(playback.current)
        first = playback.step()
        self.assertEqual(first.kind, "start")
        self.assertEqual(playback.index, 0)
        second = playback.step()
        self.assertEqual(second.kind, "visit")
        self.assertEqual(playback.index, 1)
        while not playback.finished:
            playback.step()
        final = playback.current
        self.assertEqual(final.kind, "finish")
        self.assertIs(playback.step(), final)
        playback.reset()
        self.assertEqual(playback.index, -1)
        self.assertIsNone(playback.current)

    def test_empty_playback_is_safe(self):
        from graph_steps import AlgorithmRun
        playback = Playback(AlgorithmRun("bfs", "A", (), {}, {}, ()))
        self.assertTrue(playback.finished)
        self.assertIsNone(playback.step())
        playback.reset()
        self.assertIsNone(playback.current)


if __name__ == "__main__":
    unittest.main()
