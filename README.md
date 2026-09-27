# Graph Steps

A small, dependency-free Python tool for exploring BFS, DFS, and Dijkstra on a graph. The algorithms produce replayable event snapshots; the playback cursor and Tkinter interface consume those snapshots without embedding algorithm logic in the UI.

## Requirements and run

- Python 3.10 or newer
- Tkinter (included with most standard Python distributions)

From this directory, run:

```sh
python app.py
```

The desktop window opens with a sample graph. Choose an algorithm and start node, then select **Build graph & run**. Use **Play** to start or pause, **Step** to advance one event, **Reset** to return to the beginning, and the speed slider to change playback delay. Select another graph in the sample menu, or edit the edge list directly.

For a quick demo, run the weighted sample with **Dijkstra**, press **Step** a few times, and watch distances change. Then press **Play**, resize the window, and observe that the current step remains displayed. Edit an edge or start node and build again. Keyboard users can Tab through controls; **Ctrl+Enter** builds, **Ctrl+Right** steps, and **Ctrl+R** resets. The status and node list express the same state in text as the canvas colors.

## Editing graphs

Enter one edge per line as `source target [weight]`. Weight is optional and defaults to 1. Node labels are single tokens. Blank lines and text after `#` are ignored. Toggle **Directed graph** to change edge direction.

```text
A B 2
A C 5
B C 1
B D 4
C D 1
```

BFS and DFS ignore weights. Dijkstra rejects negative weights and non-finite path distances and shows shortest-path distances. Only nodes reachable from the selected start appear in those algorithm results. Invalid syntax, non-finite weights, unknown starts, and unsupported Dijkstra weights appear beside the input controls. An empty edge list is rejected; an isolated node can be constructed through the Python API but cannot be entered in the desktop edge list.

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
- `ARCHITECTURE.md`: data flow, playback state, and size limits

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

CI runs compilation, unit tests, and a small benchmark smoke check on Python 3.10 and 3.12. To measure event generation locally:

```sh
python benchmark.py --nodes 100 --repeat 3
```

Timings vary by machine and are not CI pass thresholds. The UI is intended for small graphs; full event snapshots use memory proportional to the number of events and reached nodes.
