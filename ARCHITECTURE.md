# Architecture

`Graph` stores insertion-ordered adjacency and validates finite edge weights. `parse_graph` turns the editor's edge list into a new graph or reports a line-specific error. Each algorithm computes a complete `AlgorithmRun` before playback. Its events carry independent snapshots of visited nodes, frontier, distances, and predecessors. The dictionaries in these records are ordinary mutable Python dictionaries; callers should treat them as read-only.

`Playback` owns the event index and has no Tkinter dependency. `GraphVisualizer` owns the timer, controls, and canvas. A successful build replaces the graph and playback together. A failed build clears the previous run. Resize redraws the current playback event, and manual Step stops the timer first. Reset returns the cursor and renderer to the initial state.

The implementation stores one state snapshot per event, so time and memory grow with both graph size and event count. This is deliberate for a small teaching tool. The benchmark script measures event generation on a deterministic sparse graph; it is diagnostic and sets no machine-dependent pass threshold. Very large graphs are outside the intended UI scope.
