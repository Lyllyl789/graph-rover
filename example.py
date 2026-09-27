"""Print algorithm events as JSON lines for a small sample graph."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from graph_steps import Graph, bfs, dfs, dijkstra


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("algorithm", choices=("bfs", "dfs", "dijkstra"))
    args = parser.parse_args()

    graph = Graph(directed=True)
    for source, target, weight in (
        ("A", "B", 2), ("A", "C", 5), ("B", "C", 1),
        ("B", "D", 4), ("C", "D", 1),
    ):
        graph.add_edge(source, target, weight)
    run = {"bfs": bfs, "dfs": dfs, "dijkstra": dijkstra}[args.algorithm](graph, "A")
    for event in run.events:
        print(json.dumps(asdict(event), ensure_ascii=False))
    print(json.dumps({"order": run.order, "distances": run.distances,
                      "predecessor": run.predecessor}, ensure_ascii=False))


if __name__ == "__main__":
    main()
