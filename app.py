"""Tkinter desktop UI for replaying BFS, DFS, and Dijkstra graph events."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from graph_steps import Playback, bfs, dfs, dijkstra, parse_graph


SAMPLES = {
    "Weighted directed": "A B 2\nA C 5\nB C 1\nB D 4\nC D 1",
    "Undirected": "A B\nA C\nB D\nC D\nD E",
}
ALGORITHMS = {"BFS": bfs, "DFS": dfs, "Dijkstra": dijkstra}


class GraphVisualizer(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Graph Steps · Algorithm Visualizer")
        self.geometry("1040x720")
        self.minsize(680, 500)
        self.configure(bg="#f3f5f8")
        self.graph = None
        self.playback: Playback | None = None
        self.after_id: str | None = None
        self._build()
        self._load_sample("Weighted directed")

    def _build(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#f3f5f8")
        style.configure("TLabel", background="#f3f5f8", foreground="#243247")
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"), foreground="#17253a")
        style.configure("Hint.TLabel", foreground="#68778c")
        root = ttk.Frame(self, padding=18)
        root.pack(fill="both", expand=True)
        ttk.Label(root, text="Graph Steps", style="Title.TLabel").pack(anchor="w")
        ttk.Label(root, text="Explore BFS, DFS, and shortest paths one event at a time.",
                  style="Hint.TLabel").pack(anchor="w", pady=(2, 14))

        body = ttk.Frame(root)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=0, minsize=260)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)
        left = ttk.Frame(body, padding=(0, 0, 14, 0))
        left.grid(row=0, column=0, sticky="nsew")
        right = ttk.Frame(body)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=1)

        ttk.Label(left, text="Graph edges").pack(anchor="w")
        ttk.Label(left, text="One edge per line: source target [weight]", style="Hint.TLabel").pack(anchor="w", pady=(2, 5))
        self.editor = tk.Text(left, height=9, wrap="none", font=("Consolas", 10),
                              bg="white", fg="#243247", relief="solid", bd=1, padx=8, pady=7)
        self.editor.pack(fill="x")
        row = ttk.Frame(left)
        row.pack(fill="x", pady=7)
        self.sample = tk.StringVar(value="Weighted directed")
        picker = ttk.Combobox(row, textvariable=self.sample, values=tuple(SAMPLES), state="readonly", width=19)
        picker.pack(side="left", fill="x", expand=True)
        picker.bind("<<ComboboxSelected>>", lambda _event: self._load_sample(self.sample.get()))
        ttk.Button(row, text="Load", command=lambda: self._load_sample(self.sample.get())).pack(side="left", padx=(5, 0))
        self.directed = tk.BooleanVar(value=True)
        ttk.Checkbutton(left, text="Directed graph", variable=self.directed).pack(anchor="w", pady=(0, 9))

        options = ttk.Frame(left)
        options.pack(fill="x")
        ttk.Label(options, text="Algorithm").grid(row=0, column=0, sticky="w")
        self.algorithm = tk.StringVar(value="BFS")
        ttk.Combobox(options, textvariable=self.algorithm, values=tuple(ALGORITHMS), state="readonly", width=13).grid(row=0, column=1, sticky="ew", padx=(6, 0))
        ttk.Label(options, text="Start node").grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.start = tk.StringVar(value="A")
        ttk.Entry(options, textvariable=self.start, width=15).grid(row=1, column=1, sticky="ew", padx=(6, 0), pady=(8, 0))
        options.columnconfigure(1, weight=1)
        ttk.Button(left, text="Build graph & run", command=self._run).pack(fill="x", pady=(11, 8))
        self.error = tk.StringVar()
        ttk.Label(left, textvariable=self.error, foreground="#b42318", wraplength=245).pack(anchor="w", pady=(0, 8))
        ttk.Separator(left).pack(fill="x", pady=5)
        ttk.Label(left, text="Node status", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(5, 4))
        self.node_status = tk.StringVar(value="Build a graph to begin.")
        ttk.Label(left, textvariable=self.node_status, justify="left", wraplength=245).pack(anchor="w")

        self.canvas = tk.Canvas(right, bg="white", highlightthickness=1, highlightbackground="#dce2ea")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.bind("<Configure>", lambda _event: self._draw())
        info = ttk.Frame(right, padding=(0, 10, 0, 0))
        info.grid(row=1, column=0, sticky="ew")
        info.columnconfigure(0, weight=1)
        self.status = tk.StringVar(value="Ready · Choose an algorithm and run.")
        ttk.Label(info, textvariable=self.status).grid(row=0, column=0, sticky="w")
        controls = ttk.Frame(info)
        controls.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        self.play_button = ttk.Button(controls, text="▶ Play", command=self._toggle_play, state="disabled")
        self.play_button.pack(side="left")
        ttk.Button(controls, text="Step →", command=self._step).pack(side="left", padx=5)
        ttk.Button(controls, text="Reset", command=self._reset).pack(side="left")
        ttk.Label(controls, text="Speed").pack(side="left", padx=(16, 4))
        self.speed = tk.IntVar(value=600)
        ttk.Scale(controls, from_=150, to=1500, variable=self.speed, orient="horizontal", length=130).pack(side="left")

    def _load_sample(self, name: str) -> None:
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", SAMPLES[name])
        self.directed.set(name == "Weighted directed")

    def _run(self) -> None:
        self._stop_timer()
        try:
            graph = parse_graph(self.editor.get("1.0", "end"), self.directed.get())
            run = ALGORITHMS[self.algorithm.get()](graph, self.start.get().strip())
        except (ValueError, KeyError) as exc:
            self.error.set(str(exc))
            self.status.set("Could not build the run. Fix the input and try again.")
            return
        self.error.set("")
        self.graph = graph
        self.playback = Playback(run)
        self.play_button.configure(state="normal", text="▶ Play")
        self.status.set(f"{run.algorithm.upper()} · {len(run.events)} events · ready")
        self._draw()
        self._update_node_status(None)

    def _step(self) -> None:
        if not self.playback:
            return
        event = self.playback.step()
        self._show_event(event)
        if self.playback.finished:
            self._stop_timer()
            self.play_button.configure(text="▶ Play")

    def _toggle_play(self) -> None:
        if not self.playback:
            return
        if self.after_id is not None:
            self._stop_timer()
            self.play_button.configure(text="▶ Play")
        elif self.playback.finished:
            self.playback.reset()
            self._draw()
            self.play_button.configure(text="⏸ Pause")
            self._schedule_step()
        else:
            self.play_button.configure(text="⏸ Pause")
            self._schedule_step()

    def _schedule_step(self) -> None:
        if self.playback and self.after_id is None:
            self.after_id = self.after(max(80, int(self.speed.get())), self._on_timer)

    def _on_timer(self) -> None:
        self.after_id = None
        if not self.playback:
            return
        self._step()
        if not self.playback.finished:
            self._schedule_step()

    def _stop_timer(self) -> None:
        if self.after_id is not None:
            self.after_cancel(self.after_id)
            self.after_id = None

    def _reset(self) -> None:
        self._stop_timer()
        if self.playback:
            self.playback.reset()
        self.play_button.configure(text="▶ Play", state="normal" if self.playback else "disabled")
        self.status.set("Reset · press Play or Step to begin")
        self._draw()
        self._update_node_status(None)

    def _show_event(self, event) -> None:
        if event is None:
            return
        self.status.set(f"Step {event.sequence + 1}/{len(self.playback.run.events)} · {event.kind.replace('_', ' ')}"
                        + (f" · {event.current}" if event.current else ""))
        self._draw(event)
        self._update_node_status(event)

    def _update_node_status(self, event) -> None:
        if not self.graph:
            return
        visited = set(event.visited) if event else set()
        frontier = set(event.frontier) if event else set()
        distances = event.distances if event else {}
        lines = []
        for node in self.graph.nodes:
            labels = []
            if node in visited: labels.append("visited")
            if node in frontier: labels.append("frontier")
            if event and node == event.current: labels.append("current")
            distance = distances.get(node)
            value = "∞" if distance is None else (str(int(distance)) if distance.is_integer() else f"{distance:g}")
            lines.append(f"{node}: {', '.join(labels) or 'unseen'} · d={value}")
        self.node_status.set("\n".join(lines))

    def _draw(self, event=None) -> None:
        if not self.graph:
            return
        canvas = self.canvas
        canvas.delete("all")
        nodes = self.graph.nodes
        width, height = max(canvas.winfo_width(), 320), max(canvas.winfo_height(), 250)
        cx, cy = width / 2, height / 2
        radius = max(55, min(width, height) * 0.34)
        points = {node: (cx + radius * __import__("math").cos(-__import__("math").pi / 2 + 2 * __import__("math").pi * i / len(nodes)),
                         cy + radius * __import__("math").sin(-__import__("math").pi / 2 + 2 * __import__("math").pi * i / len(nodes)))
                  for i, node in enumerate(nodes)}
        drawn = set()
        for source, target, weight in self.graph.edges():
            key = (source, target) if self.graph.directed else frozenset((source, target))
            if key in drawn:
                continue
            drawn.add(key)
            x1, y1 = points[source]; x2, y2 = points[target]
            active = bool(event and event.kind == "inspect_edge" and (event.current, event.neighbor) == (source, target))
            color = "#e07820" if active else "#b9c3d0"
            canvas.create_line(x1, y1, x2, y2, fill=color, width=3 if active else 1.7,
                               arrow="last" if self.graph.directed else "none", arrowshape=(10, 12, 4))
            canvas.create_rectangle((x1+x2)/2-17, (y1+y2)/2-11, (x1+x2)/2+17, (y1+y2)/2+11,
                                    fill="white", outline="white")
            canvas.create_text((x1+x2)/2, (y1+y2)/2, text=f"{weight:g}", fill="#68778c", font=("Segoe UI", 9))
        visited = set(event.visited) if event else set()
        frontier = set(event.frontier) if event else set()
        for node, (x, y) in points.items():
            if event and node == event.current: fill = "#fdbb74"
            elif node in visited: fill = "#97d5b1"
            elif node in frontier: fill = "#a8c8f0"
            else: fill = "#edf1f6"
            canvas.create_oval(x-24, y-24, x+24, y+24, fill=fill, outline="#50627a", width=1.5)
            canvas.create_text(x, y, text=node, fill="#17253a", font=("Segoe UI", 10, "bold"))


if __name__ == "__main__":
    try:
        GraphVisualizer().mainloop()
    except tk.TclError as exc:
        messagebox.showerror("Could not start UI", str(exc))
