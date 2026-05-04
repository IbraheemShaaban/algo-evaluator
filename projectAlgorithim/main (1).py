"""
Algorithm Performance Evaluator
Course: Algorithms (CSE 2nd Year) – Computer and Systems Engineering
Academic Year: 2025/2026
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
import threading
import time
import random
import math
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from complexity_estimator import ComplexityEstimator
from executor import AlgorithmExecutor

# ─── Color Palette ────────────────────────────────────────────────────────────
BG        = "#0d1117"
PANEL     = "#161b22"
BORDER    = "#30363d"
ACCENT    = "#58a6ff"
ACCENT2   = "#3fb950"
ACCENT3   = "#f78166"
ACCENT4   = "#d2a8ff"
TEXT      = "#e6edf3"
TEXT_DIM  = "#8b949e"
HIGHLIGHT = "#1f6feb"
CODE_BG   = "#0d1117"
BTN_BG    = "#21262d"
BTN_HV    = "#30363d"

COMPLEXITY_COLORS = {
    "O(1)":         "#3fb950",
    "O(log n)":     "#79c0ff",
    "O(n)":         "#58a6ff",
    "O(n log n)":   "#d2a8ff",
    "O(n²)":        "#ffa657",
    "O(n³)":        "#f78166",
    "O(n² log n)":  "#ff7b72",
    "O(2^n)":       "#ff6e6e",
    "Unknown":      "#8b949e",
}


class AlgorithmEvaluatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Algorithm Performance Evaluator")
        self.geometry("1400x860")
        self.minsize(1100, 700)
        self.configure(bg=BG)
        self._setup_fonts()
        self._build_ui()
        self.mode = "manual"
        self.executor = AlgorithmExecutor()
        self.estimator = ComplexityEstimator()

    # ── Fonts ──────────────────────────────────────────────────────────────────
    def _setup_fonts(self):
        self.font_title  = font.Font(family="Consolas", size=13, weight="bold")
        self.font_mono   = font.Font(family="Consolas", size=11)
        self.font_mono_s = font.Font(family="Consolas", size=10)
        self.font_label  = font.Font(family="Consolas", size=9)
        self.font_big    = font.Font(family="Consolas", size=22, weight="bold")
        self.font_badge  = font.Font(family="Consolas", size=10, weight="bold")

    # ── Root layout ────────────────────────────────────────────────────────────
    def _build_ui(self):
        self._build_topbar()
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        body.columnconfigure(0, weight=5, minsize=420)
        body.columnconfigure(1, weight=6, minsize=480)
        body.rowconfigure(0, weight=1)
        self._build_left(body)
        self._build_right(body)
        self._build_statusbar()

    # ── Top bar ────────────────────────────────────────────────────────────────
    def _build_topbar(self):
        bar = tk.Frame(self, bg=PANEL, height=52)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        # Logo
        logo_frame = tk.Frame(bar, bg=PANEL)
        logo_frame.pack(side="left", padx=16, pady=8)
        tk.Label(logo_frame, text="Algorithm", font=self.font_title,
                 bg=PANEL, fg=TEXT).pack(side="left")
        tk.Label(logo_frame, text=" Performance ", font=self.font_title,
                 bg=PANEL, fg=ACCENT).pack(side="left")
        tk.Label(logo_frame, text="Evaluator", font=self.font_title,
                 bg=PANEL, fg=TEXT).pack(side="left")

        # Mode buttons
        mode_frame = tk.Frame(bar, bg=PANEL)
        mode_frame.pack(side="left", padx=30, pady=10)
        self.btn_manual = self._mode_btn(mode_frame, "Manual", self._set_manual)
        self.btn_manual.pack(side="left", padx=2)
        self.btn_auto   = self._mode_btn(mode_frame, "Auto",   self._set_auto)
        self.btn_auto.pack(side="left", padx=2)

        # Run button
        self.btn_run = tk.Button(
            bar, text="▶  Run Analysis", font=self.font_badge,
            bg=HIGHLIGHT, fg=TEXT, activebackground="#388bfd",
            activeforeground=TEXT, relief="flat", cursor="hand2",
            padx=16, pady=6, command=self._run_analysis
        )
        self.btn_run.pack(side="right", padx=16, pady=10)

        self._highlight_mode("manual")

    def _mode_btn(self, parent, text, cmd):
        return tk.Button(parent, text=text, font=self.font_badge,
                         bg=BTN_BG, fg=TEXT_DIM,
                         activebackground=BTN_HV, activeforeground=TEXT,
                         relief="flat", cursor="hand2", padx=14, pady=5,
                         command=cmd)

    def _highlight_mode(self, mode):
        if mode == "manual":
            self.btn_manual.config(bg=ACCENT, fg="#0d1117")
            self.btn_auto.config(bg=BTN_BG, fg=TEXT_DIM)
        else:
            self.btn_auto.config(bg=ACCENT, fg="#0d1117")
            self.btn_manual.config(bg=BTN_BG, fg=TEXT_DIM)

    # ── Left panel ─────────────────────────────────────────────────────────────
    def _build_left(self, parent):
        left = tk.Frame(parent, bg=BG)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        left.rowconfigure(0, weight=7)
        left.rowconfigure(1, weight=3)
        left.columnconfigure(0, weight=1)
        self._build_code_editor(left)
        self._build_input_panel(left)

    def _build_code_editor(self, parent):
        frame = tk.Frame(parent, bg=PANEL, relief="flat",
                         highlightthickness=1, highlightbackground=BORDER)
        frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

        # Header
        hdr = tk.Frame(frame, bg=PANEL, height=36)
        hdr.grid(row=0, column=0, sticky="ew")
        tk.Label(hdr, text="CODE EDITOR", font=self.font_label,
                 bg=PANEL, fg=TEXT_DIM).pack(side="left", padx=12, pady=8)
        tk.Label(hdr, text="Python", font=self.font_badge,
                 bg="#1f6feb", fg=TEXT, padx=6).pack(side="left", pady=8)

        # Line numbers + text area
        editor_frame = tk.Frame(frame, bg=CODE_BG)
        editor_frame.grid(row=1, column=0, sticky="nsew")
        editor_frame.rowconfigure(0, weight=1)
        editor_frame.columnconfigure(1, weight=1)

        self.line_numbers = tk.Text(
            editor_frame, width=4, bg="#161b22", fg=TEXT_DIM,
            font=self.font_mono_s, state="disabled", relief="flat",
            padx=4, pady=4, cursor="arrow", selectbackground="#161b22"
        )
        self.line_numbers.grid(row=0, column=0, sticky="ns")

        self.code_editor = tk.Text(
            editor_frame, bg=CODE_BG, fg=TEXT, font=self.font_mono,
            insertbackground=ACCENT, relief="flat", padx=8, pady=4,
            wrap="none", undo=True, selectbackground=HIGHLIGHT,
            tabs=("4c",)
        )
        self.code_editor.grid(row=0, column=1, sticky="nsew")

        vsb = ttk.Scrollbar(editor_frame, orient="vertical",
                            command=self._sync_scroll)
        vsb.grid(row=0, column=2, sticky="ns")
        self.code_editor.config(yscrollcommand=vsb.set)

        self.code_editor.bind("<KeyRelease>", self._update_line_numbers)
        self.code_editor.bind("<MouseWheel>", self._update_line_numbers)

        template = (
            "# Write your algorithm inside this function\n"
            "def my_algorithm(arr):\n"
            "    n = len(arr)\n"
            "    # Your code here\n"
            "    for i in range(n):\n"
            "        for j in range(i + 1, n):\n"
            "            if arr[i] > arr[j]:\n"
            "                arr[i], arr[j] = arr[j], arr[i]\n"
            "    return arr\n"
            "\n"
            "# arr is injected automatically\n"
        )
        self.code_editor.insert("1.0", template)
        self._update_line_numbers()

    def _sync_scroll(self, *args):
        self.code_editor.yview(*args)
        self._update_line_numbers()

    def _update_line_numbers(self, event=None):
        lines = int(self.code_editor.index("end-1c").split(".")[0])
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", "end")
        for i in range(1, lines + 1):
            self.line_numbers.insert("end", f"{i}\n")
        self.line_numbers.config(state="disabled")

    def _build_input_panel(self, parent):
        frame = tk.Frame(parent, bg=PANEL, relief="flat",
                         highlightthickness=1, highlightbackground=BORDER)
        frame.grid(row=1, column=0, sticky="nsew")
        frame.columnconfigure(1, weight=1)

        tk.Label(frame, text="ARRAY INPUT", font=self.font_label,
                 bg=PANEL, fg=TEXT_DIM).grid(row=0, column=0, columnspan=3,
                                              sticky="w", padx=12, pady=(8, 2))

        tk.Label(frame, text="n =", font=self.font_mono, bg=PANEL, fg=TEXT)\
            .grid(row=1, column=0, padx=(12, 4), pady=4, sticky="w")

        self.size_var = tk.StringVar(value="9")
        size_entry = tk.Entry(frame, textvariable=self.size_var, width=6,
                              bg=BTN_BG, fg=TEXT, font=self.font_mono,
                              insertbackground=ACCENT, relief="flat",
                              highlightthickness=1, highlightbackground=BORDER)
        size_entry.grid(row=1, column=1, sticky="w", padx=4, pady=4)

        tk.Button(frame, text="Generate Random", font=self.font_label,
                  bg=BTN_BG, fg=TEXT_DIM, relief="flat", cursor="hand2",
                  padx=8, command=self._generate_random)\
            .grid(row=1, column=2, padx=8, pady=4)

        tk.Label(frame, text="Array values (comma separated):",
                 font=self.font_label, bg=PANEL, fg=TEXT_DIM)\
            .grid(row=2, column=0, columnspan=3, sticky="w", padx=12, pady=(4, 2))

        self.array_entry = tk.Entry(
            frame, bg=BTN_BG, fg=TEXT, font=self.font_mono_s,
            insertbackground=ACCENT, relief="flat",
            highlightthickness=1, highlightbackground=BORDER
        )
        self.array_entry.grid(row=3, column=0, columnspan=3,
                               sticky="ew", padx=12, pady=(0, 8))
        self.array_entry.insert(0, "5, 2, 9, 1, 7, 3, 8, 4, 6")

        # Manual mode specific label
        self.manual_label = tk.Label(
            frame, text="● Manual mode – provide your own array",
            font=self.font_label, bg=PANEL, fg=ACCENT2
        )
        self.manual_label.grid(row=4, column=0, columnspan=3,
                                sticky="w", padx=12, pady=(0, 6))

        # Auto mode info
        self.auto_label = tk.Label(
            frame,
            text="● Auto mode – sizes: 10, 50, 100, 500, 1000 (best/avg/worst)",
            font=self.font_label, bg=PANEL, fg=ACCENT4
        )

    # ── Right panel ────────────────────────────────────────────────────────────
    def _build_right(self, parent):
        right = tk.Frame(parent, bg=BG)
        right.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        right.rowconfigure(0, weight=1)
        right.columnconfigure(0, weight=1)

        container = tk.Frame(right, bg=PANEL, relief="flat",
                             highlightthickness=1, highlightbackground=BORDER)
        container.grid(row=0, column=0, sticky="nsew")
        container.rowconfigure(1, weight=1)
        container.columnconfigure(0, weight=1)

        # Header
        hdr = tk.Frame(container, bg=PANEL, height=36)
        hdr.grid(row=0, column=0, sticky="ew")
        tk.Label(hdr, text="ANALYSIS RESULTS", font=self.font_label,
                 bg=PANEL, fg=TEXT_DIM).pack(side="left", padx=12, pady=8)

        # Scrollable results area
        canvas_outer = tk.Canvas(container, bg=PANEL, highlightthickness=0)
        canvas_outer.grid(row=1, column=0, sticky="nsew")
        vsb = ttk.Scrollbar(container, orient="vertical",
                            command=canvas_outer.yview)
        vsb.grid(row=1, column=1, sticky="ns")
        canvas_outer.configure(yscrollcommand=vsb.set)

        self.results_frame = tk.Frame(canvas_outer, bg=PANEL)
        self.results_frame.columnconfigure(0, weight=1)
        win_id = canvas_outer.create_window((0, 0), window=self.results_frame,
                                            anchor="nw")

        def _on_configure(e):
            canvas_outer.configure(scrollregion=canvas_outer.bbox("all"))
            canvas_outer.itemconfig(win_id, width=canvas_outer.winfo_width())

        self.results_frame.bind("<Configure>", _on_configure)
        canvas_outer.bind("<Configure>", _on_configure)

        self._build_results_placeholder()

    def _build_results_placeholder(self):
        for w in self.results_frame.winfo_children():
            w.destroy()
        tk.Label(
            self.results_frame,
            text="Run an analysis to see results here.",
            font=self.font_mono, bg=PANEL, fg=TEXT_DIM
        ).pack(pady=60)

    def _build_results(self, complexity, candidate_scores, times_data, mode):
        for w in self.results_frame.winfo_children():
            w.destroy()

        color = COMPLEXITY_COLORS.get(complexity, TEXT_DIM)

        # ── Detected complexity badge ──
        badge_frame = tk.Frame(self.results_frame, bg=PANEL)
        badge_frame.pack(fill="x", padx=16, pady=(14, 4))
        tk.Label(badge_frame, text="DETECTED COMPLEXITY",
                 font=self.font_label, bg=PANEL, fg=TEXT_DIM)\
            .pack(anchor="w")
        tk.Label(badge_frame, text=complexity,
                 font=self.font_big, bg=PANEL, fg=color)\
            .pack(anchor="w")

        desc = self._complexity_description(complexity)
        tk.Label(badge_frame, text=desc, font=self.font_label,
                 bg=PANEL, fg=TEXT_DIM, wraplength=420, justify="left")\
            .pack(anchor="w", pady=(0, 4))

        # Confidence bar
        top_score  = max(candidate_scores.values()) if candidate_scores else 1
        confidence = int((top_score / max(top_score, 1)) * 100)
        self._confidence_bar(badge_frame, confidence, color)

        sep(self.results_frame)

        # ── Candidate classes ──
        tk.Label(self.results_frame, text="CANDIDATE CLASSES",
                 font=self.font_label, bg=PANEL, fg=TEXT_DIM)\
            .pack(anchor="w", padx=16, pady=(8, 4))

        sorted_candidates = sorted(candidate_scores.items(),
                                   key=lambda x: x[1], reverse=True)[:5]
        max_s = sorted_candidates[0][1] if sorted_candidates else 1
        for cplx, score in sorted_candidates:
            c = COMPLEXITY_COLORS.get(cplx, TEXT_DIM)
            ratio = score / max_s if max_s else 0
            self._candidate_row(self.results_frame, cplx, ratio, c)

        sep(self.results_frame)

        # ── Chart ──
        tk.Label(self.results_frame, text="RUNTIME ACROSS INPUT SIZES",
                 font=self.font_label, bg=PANEL, fg=TEXT_DIM)\
            .pack(anchor="w", padx=16, pady=(8, 4))

        self._draw_chart(times_data, mode, complexity, color)

        # ── Case table (auto mode) ──
        if mode == "auto" and isinstance(times_data, dict) and "best" in times_data:
            sep(self.results_frame)
            self._draw_case_table(times_data)

    def _confidence_bar(self, parent, pct, color):
        bar_bg = tk.Frame(parent, bg=BORDER, height=6)
        bar_bg.pack(fill="x", pady=(4, 0))
        bar_bg.pack_propagate(False)
        tk.Frame(bar_bg, bg=color, height=6,
                 width=int(pct * 3)).pack(side="left")
        tk.Label(parent, text=f"Confidence: {pct}%",
                 font=self.font_label, bg=PANEL, fg=TEXT_DIM)\
            .pack(anchor="w")

    def _candidate_row(self, parent, label, ratio, color):
        row = tk.Frame(parent, bg=PANEL)
        row.pack(fill="x", padx=16, pady=2)
        tk.Label(row, text=label, font=self.font_label,
                 bg=PANEL, fg=color, width=14, anchor="w")\
            .pack(side="left")
        bar_bg = tk.Frame(row, bg=BORDER, height=8)
        bar_bg.pack(side="left", fill="x", expand=True, padx=4)
        bar_bg.pack_propagate(False)
        tk.Frame(bar_bg, bg=color, height=8).place(relwidth=ratio, relheight=1)

    def _draw_chart(self, times_data, mode, complexity, color):
        fig = Figure(figsize=(5, 2.6), facecolor=PANEL, dpi=96)
        ax  = fig.add_subplot(111)
        ax.set_facecolor(CODE_BG)
        ax.tick_params(colors=TEXT_DIM, labelsize=8)
        for spine in ax.spines.values():
            spine.set_edgecolor(BORDER)
        ax.set_xlabel("Input Size (n)", color=TEXT_DIM, fontsize=8)
        ax.set_ylabel("Time (ms)", color=TEXT_DIM, fontsize=8)
        ax.grid(color=BORDER, linestyle="--", linewidth=0.5, alpha=0.5)

        if mode == "manual":
            sizes = times_data.get("sizes", [])
            times = times_data.get("times", [])
            if sizes and times:
                ax.plot(sizes, [t * 1000 for t in times],
                        color=color, linewidth=2, marker="o", markersize=4)
        else:
            for case, (cname, ccolor) in [
                ("best",  ("BEST",  ACCENT2)),
                ("avg",   ("AVG",   ACCENT)),
                ("worst", ("WORST", ACCENT3)),
            ]:
                d = times_data.get(case, {})
                sx = sorted(d.keys())
                ty = [d[s] * 1000 for s in sx]
                if sx:
                    ax.plot(sx, ty, color=ccolor, linewidth=2,
                            label=cname, marker="o", markersize=3)
            ax.legend(facecolor=PANEL, edgecolor=BORDER,
                      labelcolor=TEXT, fontsize=7)

        fig.tight_layout(pad=0.6)
        canvas = FigureCanvasTkAgg(fig, master=self.results_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", padx=16, pady=4)

        if mode == "auto":
            self._case_labels(self.results_frame, times_data)

    def _case_labels(self, parent, times_data):
        row = tk.Frame(parent, bg=PANEL)
        row.pack(fill="x", padx=16, pady=(0, 8))
        for label, key, color in [("BEST", "best", ACCENT2),
                                   ("AVG",  "avg",  ACCENT),
                                   ("WORST","worst", ACCENT3)]:
            col = tk.Frame(row, bg=PANEL)
            col.pack(side="left", expand=True)
            tk.Label(col, text=label, font=self.font_label,
                     bg=PANEL, fg=TEXT_DIM).pack()
            tk.Label(col, text=times_data.get(f"{key}_complexity", "–"),
                     font=self.font_badge, bg=PANEL, fg=color).pack()

    def _draw_case_table(self, times_data):
        tk.Label(self.results_frame, text="TIMING TABLE (ms)",
                 font=self.font_label, bg=PANEL, fg=TEXT_DIM)\
            .pack(anchor="w", padx=16, pady=(8, 4))

        table = tk.Frame(self.results_frame, bg=PANEL)
        table.pack(fill="x", padx=16, pady=(0, 12))

        headers = ["Size", "Best", "Average", "Worst"]
        colors  = [TEXT_DIM, ACCENT2, ACCENT, ACCENT3]
        for c, (h, col) in enumerate(zip(headers, colors)):
            tk.Label(table, text=h, font=self.font_badge, bg=BORDER,
                     fg=col, width=10, pady=4)\
                .grid(row=0, column=c, sticky="ew", padx=1, pady=1)

        sizes = sorted(set(list(times_data.get("best", {}).keys()) +
                           list(times_data.get("avg",  {}).keys()) +
                           list(times_data.get("worst",{}).keys())))
        for r, s in enumerate(sizes, 1):
            bg = CODE_BG if r % 2 == 0 else "#111519"
            tk.Label(table, text=str(s), font=self.font_mono_s,
                     bg=bg, fg=TEXT, width=10, pady=3)\
                .grid(row=r, column=0, sticky="ew", padx=1, pady=1)
            for c, key in enumerate(["best", "avg", "worst"], 1):
                val = times_data.get(key, {}).get(s)
                txt = f"{val*1000:.3f}" if val is not None else "—"
                tk.Label(table, text=txt, font=self.font_mono_s,
                         bg=bg, fg=TEXT_DIM, width=10, pady=3)\
                    .grid(row=r, column=c, sticky="ew", padx=1, pady=1)

    # ── Status bar ─────────────────────────────────────────────────────────────
    def _build_statusbar(self):
        bar = tk.Frame(self, bg="#111519", height=26)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(bar, textvariable=self.status_var, font=self.font_label,
                 bg="#111519", fg=TEXT_DIM, anchor="w")\
            .pack(side="left", padx=12)
        self.progress = ttk.Progressbar(bar, mode="indeterminate",
                                         length=120, style="Green.Horizontal.TProgressbar")
        self.progress.pack(side="right", padx=12, pady=4)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Green.Horizontal.TProgressbar",
                        background=ACCENT, troughcolor=BORDER, borderwidth=0)
        style.configure("Vertical.TScrollbar", background=PANEL,
                        troughcolor=BG, borderwidth=0, arrowcolor=TEXT_DIM)
        style.configure("Horizontal.TScrollbar", background=PANEL,
                        troughcolor=BG, borderwidth=0, arrowcolor=TEXT_DIM)

    # ── Mode switching ─────────────────────────────────────────────────────────
    def _set_manual(self):
        self.mode = "manual"
        self._highlight_mode("manual")
        self.manual_label.grid(row=4, column=0, columnspan=3,
                               sticky="w", padx=12, pady=(0, 6))
        self.auto_label.grid_remove()
        self.array_entry.config(state="normal")

    def _set_auto(self):
        self.mode = "auto"
        self._highlight_mode("auto")
        self.auto_label.grid(row=4, column=0, columnspan=3,
                             sticky="w", padx=12, pady=(0, 6))
        self.manual_label.grid_remove()
        self.array_entry.config(state="disabled")

    # ── Helpers ────────────────────────────────────────────────────────────────
    def _generate_random(self):
        try:
            n = int(self.size_var.get())
        except ValueError:
            n = 10
        arr = [random.randint(1, 100) for _ in range(n)]
        self.array_entry.config(state="normal")
        self.array_entry.delete(0, "end")
        self.array_entry.insert(0, ", ".join(map(str, arr)))
        if self.mode == "auto":
            self.array_entry.config(state="disabled")

    def _complexity_description(self, c):
        descs = {
            "O(1)":       "Constant — result independent of input size.",
            "O(log n)":   "Logarithmic — halves the problem each step.",
            "O(n)":       "Linear — one pass through the data.",
            "O(n log n)": "Linearithmic — efficient sort-like behaviour.",
            "O(n²)":      "Quadratic — nested loop pattern detected.",
            "O(n³)":      "Cubic — triple nested loops.",
            "O(n² log n)":"Slightly worse than quadratic.",
            "O(2^n)":     "Exponential — doubles work with each element.",
            "Unknown":    "Could not determine complexity class reliably.",
        }
        return descs.get(c, "")

    # ── Run analysis ───────────────────────────────────────────────────────────
    def _run_analysis(self):
        code = self.code_editor.get("1.0", "end-1c")
        if not code.strip():
            messagebox.showerror("Error", "Code editor is empty.")
            return
        self.btn_run.config(state="disabled")
        self.progress.start(12)
        self.status_var.set("Running analysis…")
        t = threading.Thread(target=self._analysis_worker,
                             args=(code,), daemon=True)
        t.start()

    def _analysis_worker(self, code):
        try:
            if self.mode == "manual":
                raw = self.array_entry.get()
                try:
                    arr = [float(x) for x in raw.split(",") if x.strip()]
                except ValueError:
                    self.after(0, lambda: messagebox.showerror(
                        "Error", "Invalid array – use comma-separated numbers."))
                    return
                sizes = [10, 50, 100, 200, 500, 1000]
                all_times = {}
                for s in sizes:
                    test_arr = (arr * (s // len(arr) + 1))[:s] if arr else \
                               [random.randint(1, 100) for _ in range(s)]
                    t = self.executor.time_it(code, test_arr)
                    if t is not None:
                        all_times[s] = t
                times_data = {
                    "sizes": list(all_times.keys()),
                    "times": list(all_times.values()),
                }
                complexity, candidate_scores = \
                    self.estimator.estimate(list(all_times.keys()),
                                           list(all_times.values()))
            else:
                sizes  = [500, 1000, 1500, 2000, 2500, 3000]
                cases  = {"best": {}, "avg": {}, "worst": {}}
                for s in sizes:
                    best_arr  = list(range(s))
                    worst_arr = list(range(s, 0, -1))
                    avg_arr   = [random.randint(1, s) for _ in range(s)]
                    for case, arr in [("best",  best_arr),
                                      ("avg",   avg_arr),
                                      ("worst", worst_arr)]:
                        t = self.executor.time_it(code, arr[:])
                        if t is not None:
                            cases[case][s] = t
                # Estimate per case
                for case in ["best", "avg", "worst"]:
                    d = cases[case]
                    if d:
                        sx = sorted(d.keys()); ty = [d[k] for k in sx]
                        cplx, _ = self.estimator.estimate(sx, ty)
                        cases[f"{case}_complexity"] = cplx
                # Overall: use average
                avg_d  = cases["avg"]
                sx     = sorted(avg_d.keys())
                ty     = [avg_d[k] for k in sx]
                complexity, candidate_scores = self.estimator.estimate(sx, ty)
                times_data = cases

            mode = self.mode
            self.after(0, lambda: self._show_results(
                complexity, candidate_scores, times_data, mode))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Runtime Error", str(e)))
        finally:
            self.after(0, self._analysis_done)

    def _show_results(self, complexity, candidate_scores, times_data, mode):
        self._build_results(complexity, candidate_scores, times_data, mode)
        self.status_var.set(
            f"Analysis complete – Detected: {complexity}")

    def _analysis_done(self):
        self.progress.stop()
        self.btn_run.config(state="normal")


# ── Separator helper ───────────────────────────────────────────────────────────
def sep(parent):
    tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", padx=16, pady=6)


if __name__ == "__main__":
    app = AlgorithmEvaluatorApp()
    app.mainloop()
