# Graph Algorithm Steps — phase 1

A small, dependency-free Python prototype for replaying graph algorithms as events.
It is a local deliverable, not an initialized Git repository.

## Run

Requires Python 3.10 or newer.

```sh
python example.py bfs
python example.py dfs
python example.py dijkstra
python -m unittest discover -s tests -v
```

Each command prints a JSON event per line, followed by the traversal result.
Node labels are strings. Edges may be directed or undirected; weights must be
finite numbers. BFS and DFS ignore edge weights. Dijkstra requires nonnegative
weights and returns shortest distances and predecessors.

## Layout

- `graph_steps/graph.py`: graph data model and validation
- `graph_steps/events.py`: replayable step event and algorithm result
- `graph_steps/algorithms.py`: BFS, DFS, Dijkstra
- `example.py`: minimal event-stream demo
- `tests/`: behavior tests

Events contain snapshots (`frontier`, `visited`, `distances`) so a future UI can
render any step without reconstructing earlier state. `start`, `visit`,
`inspect_edge`, `relax`, and `finish` are the shared event types. The graph's
insertion order determines BFS/DFS tie breaks; Dijkstra uses insertion order
for equal-distance choices.
