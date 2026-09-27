# Graph Steps

A small, dependency-free Python tool for exploring BFS, DFS, and Dijkstra on a graph. The algorithms produce immutable event snapshots; the playback cursor and Tkinter interface consume those snapshots without embedding algorithm logic in the UI.

## Requirements and run

- Python 3.10 or newer
- Tkinter (included with most standard Python distributions)

From this directory, run:

```sh
python app.py
```

The desktop window opens with a sample graph. Choose an algorithm and start node, then select **Build graph & run**. Use **Play** to start or pause, **Step** to advance one event, **Reset** to return to the beginning, and the speed slider to change playback delay. Select another graph in the sample menu, or edit the edge list directly.

## Editing graphs

Enter one edge per line as `source target [weight]`. Weight is optional and defaults to 1. Node labels are single tokens. Blank lines and text after `#` are ignored. Toggle **Directed graph** to change edge direction.

```text
A B 2
A C 5
B C 1
B D 4
C D 1
```

BFS and DFS ignore weights. Dijkstra rejects negative weights and shows shortest-path distances. Only nodes reachable from the selected start appear in those algorithm results. Invalid syntax, unknown starts, and unsupported Dijkstra weights appear beside the input controls.

## What the display shows

- Orange node: current node; green: visited; blue: frontier; gray: unseen.
- The orange edge marks the edge being inspected.
- The node list shows each node's state and current distance (`∞` when not reached yet).
- The status line shows the event kind and position in the run.

The canvas and controls resize with the window. Small screens can use the minimum window size and scroll is not needed for the sample graphs.

## Modules

- `graph_steps/graph.py`: graph data model and validation
- `graph_steps/algorithms.py`: BFS, DFS, Dijkstra event generation
- `graph_steps/events.py`: immutable event and run records
- `graph_steps/playback.py`: UI-independent step cursor and reset
- `graph_steps/input.py`: edge-list parsing and input errors
- `app.py`: Tkinter controls and canvas renderer

The original JSON-lines demonstration remains available:

```sh
python example.py bfs
python example.py dfs
python example.py dijkstra
```

## Tests

```sh
python -m unittest discover -s tests -v
```

The tests cover algorithm outputs, event snapshots, edge-list parsing, and playback cursor behavior. GUI interaction still benefits from a manual check on the target desktop and Python/Tk version.
