"""Parser for the compact edge-list format used by the desktop interface."""

from __future__ import annotations

from .graph import Graph


def parse_graph(text: str, directed: bool = False) -> Graph:
    """Parse one `source target [weight]` edge per line; # starts a comment."""
    graph = Graph(directed=directed)
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) not in (2, 3):
            raise ValueError(f"line {line_number}: expected `source target [weight]`")
        source, target = parts[:2]
        try:
            weight = float(parts[2]) if len(parts) == 3 else 1.0
        except ValueError as exc:
            raise ValueError(f"line {line_number}: weight must be a number") from exc
        try:
            graph.add_edge(source, target, weight)
        except ValueError as exc:
            raise ValueError(f"line {line_number}: {exc}") from exc
    if not graph.nodes:
        raise ValueError("enter at least one edge to build a graph")
    return graph
