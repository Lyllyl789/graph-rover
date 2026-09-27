"""Deterministic BFS, DFS, and Dijkstra runs with state snapshots."""

from __future__ import annotations

from collections import deque
from collections.abc import Iterator
import math

from .events import AlgorithmRun, EventKind, StepEvent
from .graph import Graph


class _Recorder:
    def __init__(self, algorithm: str, start: str) -> None:
        self.algorithm = algorithm
        self.start = start
        self.order: list[str] = []
        self.distances: dict[str, float] = {start: 0.0}
        self.predecessor: dict[str, str | None] = {start: None}
        self.events: list[StepEvent] = []

    def emit(self, kind: EventKind, current: str | None,
             neighbor: str | None = None, frontier: tuple[str, ...] = ()) -> None:
        self.events.append(StepEvent(
            sequence=len(self.events), algorithm=self.algorithm, kind=kind,
            current=current, neighbor=neighbor, frontier=frontier,
            visited=tuple(self.order), distances=dict(self.distances),
            predecessor=dict(self.predecessor),
        ))

    def finish(self) -> AlgorithmRun:
        self.emit("finish", None)
        return AlgorithmRun(self.algorithm, self.start, tuple(self.order),
                            dict(self.distances), dict(self.predecessor),
                            tuple(self.events))


def bfs(graph: Graph, start: str) -> AlgorithmRun:
    """Traverse reachable nodes in breadth-first order."""
    graph.require_node(start)
    run = _Recorder("bfs", start)
    queue = deque([start])
    discovered = {start}
    run.emit("start", start, frontier=tuple(queue))
    while queue:
        current = queue.popleft()
        run.order.append(current)
        run.emit("visit", current, frontier=tuple(queue))
        for neighbor, _ in graph.neighbors(current):
            run.emit("inspect_edge", current, neighbor, tuple(queue))
            if neighbor not in discovered:
                discovered.add(neighbor)
                run.distances[neighbor] = run.distances[current] + 1
                run.predecessor[neighbor] = current
                queue.append(neighbor)
                run.emit("relax", current, neighbor, tuple(queue))
    return run.finish()


def dfs(graph: Graph, start: str) -> AlgorithmRun:
    """Traverse reachable nodes in depth-first order without recursion."""
    graph.require_node(start)
    run = _Recorder("dfs", start)
    # Frames retain neighbor position, preserving insertion-order DFS.
    stack: list[tuple[str, Iterator[tuple[str, float]]]] = []
    seen = {start}
    stack.append((start, iter(graph.neighbors(start))))
    run.emit("start", start, frontier=(start,))
    run.order.append(start)
    run.emit("visit", start, frontier=(start,))
    while stack:
        current, neighbors = stack[-1]
        try:
            neighbor, _ = next(neighbors)
        except StopIteration:
            stack.pop()
            continue
        run.emit("inspect_edge", current, neighbor,
                 tuple(node for node, _ in stack))
        if neighbor in seen:
            continue
        seen.add(neighbor)
        run.distances[neighbor] = run.distances[current] + 1
        run.predecessor[neighbor] = current
        stack.append((neighbor, iter(graph.neighbors(neighbor))))
        frontier = tuple(node for node, _ in stack)
        run.emit("relax", current, neighbor, frontier)
        run.order.append(neighbor)
        run.emit("visit", neighbor, frontier=frontier)
    return run.finish()


def dijkstra(graph: Graph, start: str) -> AlgorithmRun:
    """Find shortest paths from start; reject any negative edge weight."""
    graph.require_node(start)
    if any(weight < 0 for _, _, weight in graph.edges()):
        raise ValueError("Dijkstra requires nonnegative edge weights")
    run = _Recorder("dijkstra", start)
    settled: set[str] = set()

    def frontier() -> tuple[str, ...]:
        # Graph insertion order resolves equal-distance ties.
        return tuple(sorted((node for node in graph.nodes
                             if node not in settled and node in run.distances),
                            key=lambda node: run.distances[node]))

    run.emit("start", start, frontier=frontier())
    while frontier():
        current = frontier()[0]
        settled.add(current)
        run.order.append(current)
        run.emit("visit", current, frontier=frontier())
        for neighbor, weight in graph.neighbors(current):
            run.emit("inspect_edge", current, neighbor, frontier())
            if neighbor in settled:
                continue
            candidate = run.distances[current] + weight
            if not math.isfinite(candidate):
                raise ValueError("shortest-path distance exceeds finite numeric range")
            if neighbor not in run.distances or candidate < run.distances[neighbor]:
                run.distances[neighbor] = candidate
                run.predecessor[neighbor] = current
                run.emit("relax", current, neighbor, frontier())
    return run.finish()
