"""Small reproducible timing sample for graph event generation, not a CI speed gate."""

from __future__ import annotations

import argparse
from statistics import median
from time import perf_counter

from graph_steps import Graph, bfs, dfs, dijkstra


def make_graph(nodes: int) -> Graph:
    graph = Graph(directed=True)
    for index in range(nodes):
        source = str(index)
        graph.add_node(source)
        for offset in (1, 2, 5):
            if index + offset < nodes:
                graph.add_edge(source, str(index + offset), offset)
    return graph


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nodes", type=int, default=100)
    parser.add_argument("--repeat", type=int, default=3)
    args = parser.parse_args()
    if args.nodes < 1 or args.repeat < 1:
        parser.error("--nodes and --repeat must be positive")
    graph = make_graph(args.nodes)
    print(f"nodes={args.nodes} arcs={len(graph.edges())} repeat={args.repeat}")
    for algorithm in (bfs, dfs, dijkstra):
        samples = []
        for _ in range(args.repeat):
            start = perf_counter()
            run = algorithm(graph, "0")
            samples.append((perf_counter() - start) * 1000)
        print(f"{algorithm.__name__}: median={median(samples):.2f} ms "
              f"events={len(run.events)} reached={len(run.order)}")


if __name__ == "__main__":
    main()
