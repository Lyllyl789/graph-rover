"""A small graph model with deterministic neighbor order."""

from __future__ import annotations

import math


class Graph:
    def __init__(self, directed: bool = False) -> None:
        self.directed = directed
        self._adjacency: dict[str, dict[str, float]] = {}

    def add_node(self, node: str) -> None:
        if not isinstance(node, str) or not node:
            raise ValueError("node labels must be nonempty strings")
        self._adjacency.setdefault(node, {})

    def add_edge(self, source: str, target: str, weight: float = 1.0) -> None:
        if isinstance(weight, bool) or not isinstance(weight, (int, float)) or not math.isfinite(weight):
            raise ValueError("edge weights must be finite numbers")
        self.add_node(source)
        self.add_node(target)
        self._adjacency[source][target] = float(weight)
        if not self.directed:
            self._adjacency[target][source] = float(weight)

    @property
    def nodes(self) -> tuple[str, ...]:
        return tuple(self._adjacency)

    def neighbors(self, node: str) -> tuple[tuple[str, float], ...]:
        self.require_node(node)
        return tuple(self._adjacency[node].items())

    def require_node(self, node: str) -> None:
        if node not in self._adjacency:
            raise ValueError(f"unknown node: {node!r}")

    def edges(self) -> tuple[tuple[str, str, float], ...]:
        """Return directed arcs; undirected edges appear in both directions."""
        return tuple((source, target, weight)
                     for source, neighbors in self._adjacency.items()
                     for target, weight in neighbors.items())
