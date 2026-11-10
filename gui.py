import os
import json
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# Connect real algorithm modules
from ga import run_ga
from woc import run_woc


class ColorfulNQueensGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("N-Queens: GA vs. Wisdom of Artificial Crowds")
        self.root.geometry("1180x760")

        # Color Palette Definitions
        self.BG_MAIN = "#1E1E2E"       # Deep Purple/Dark Background
        self.BG_CARD = "#2B2B3D"       # Dark Slate Card Accent
        self.TEXT_COLOR = "#F8F8F2"    # Bright Off-White
        self.ACCENT_PURPLE = "#BD93F9"  # Neon Purple
        self.ACCENT_PINK = "#FF79C6"    # Vibrant Pink
        self.ACCENT_CYAN = "#8BE9FD"    # Electric Cyan
        self.ACCENT_GREEN = "#50FA7B"   # Neon Mint Green
        self.ACCENT_YELLOW = "#F1FA8C"  # Neon Yellow

        self.root.configure(bg=self.BG_MAIN)
        self.setup_styles()

        # Header & Controls Bar
        header_frame = tk.Frame(root, bg=self.BG_CARD, bd=0, highlightthickness=2,
                                highlightbackground=self.ACCENT_PURPLE)
        header_frame.pack(side=tk.TOP, fill=tk.X, padx=15, pady=12)

        title_lbl = tk.Label(
            header_frame,
            text="N-QUEENS SOLVER VISUALIZER",
            font=("Helvetica", 14, "bold"),
            fg=self.ACCENT_CYAN,
            bg=self.BG_CARD
        )
        title_lbl.pack(side=tk.TOP, anchor=tk.W, padx=15, pady=(8, 4))

        controls_box = tk.Frame(header_frame, bg=self.BG_CARD)
        controls_box.pack(side=tk.TOP, fill=tk.X, padx=15, pady=(0, 10))

        # 1. Dataset File Dropdown (Scans data/ directory)
        tk.Label(controls_box, text="Test File:", fg=self.TEXT_COLOR, bg=self.BG_CARD,
                 font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5)
        self.data_files = self.get_available_datasets()
        self.combo_file = ttk.Combobox(controls_box, values=self.data_files, width=22, state="readonly")
        if self.data_files:
            self.combo_file.set(self.data_files[0])
            self.combo_file.bind("<<ComboboxSelected>>", self.on_file_selected)
        else:
            self.combo_file.set("No data files found")
        self.combo_file.grid(row=0, column=1, padx=5)

        # 2. Board Size (N) Dropdown
        tk.Label(controls_box, text="Board Size (N):", fg=self.TEXT_COLOR, bg=self.BG_CARD,
                 font=("Arial", 10, "bold")).grid(row=0, column=2, padx=5)
        self.combo_n = ttk.Combobox(controls_box, values=[8, 16, 32, 64, 128, 256], width=6, state="readonly")
        self.combo_n.set(8)
        self.combo_n.grid(row=0, column=3, padx=5)

        # 3. Crowd Size (k) Dropdown
        tk.Label(controls_box, text="Crowd (k):", fg=self.TEXT_COLOR, bg=self.BG_CARD,
                 font=("Arial", 10, "bold")).grid(row=0, column=4, padx=5)
        self.combo_k = ttk.Combobox(controls_box, values=[5, 10, 20], width=5, state="readonly")
        self.combo_k.set(10)
        self.combo_k.grid(row=0, column=5, padx=5)

        # 4. Seed Input
        tk.Label(controls_box, text="Seed:", fg=self.TEXT_COLOR, bg=self.BG_CARD, font=("Arial", 10, "bold")).grid(
            row=0, column=6, padx=5)
        self.entry_seed = tk.Entry(controls_box, width=8, bg="#383A59", fg=self.TEXT_COLOR, insertbackground="white",
                                   font=("Arial", 10, "bold"))
        self.entry_seed.insert(0, "42")
        self.entry_seed.grid(row=0, column=7, padx=5)

        # 5. Run Button
        self.btn_run = tk.Button(
            controls_box, text="RUN COMPARISON", font=("Arial", 10, "bold"),
            bg=self.ACCENT_PINK, fg="black", activebackground=self.ACCENT_PURPLE,
            relief=tk.FLAT, padx=12, pady=3, command=self.on_run, cursor="hand2"
        )
        self.btn_run.grid(row=0, column=8, padx=12)

        # Main Workspace
        workspace_frame = tk.Frame(root, bg=self.BG_MAIN)
        workspace_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        boards_container = tk.Frame(workspace_frame, bg=self.BG_MAIN)
        boards_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Standard GA Board Box
        ga_frame = tk.LabelFrame(
            boards_container, text="Standard GA Solution ",
            fg=self.ACCENT_PINK, bg=self.BG_CARD, font=("Arial", 11, "bold"), bd=2
        )
        ga_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.canvas_ga = tk.Canvas(ga_frame, width=320, height=320, bg="#191A21", highlightthickness=0)
        self.canvas_ga.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # GA + WoC Board Box
        woc_frame = tk.LabelFrame(
            boards_container, text="GA + WoC Solution ",
            fg=self.ACCENT_GREEN, bg=self.BG_CARD, font=("Arial", 11, "bold"), bd=2
        )
        woc_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        self.canvas_woc = tk.Canvas(woc_frame, width=320, height=320, bg="#191A21", highlightthickness=0)
        self.canvas_woc.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Right Panel: Graph & Status Bar
        right_panel = tk.Frame(workspace_frame, bg=self.BG_MAIN)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        graph_box = tk.LabelFrame(
            right_panel, text="Convergence Real-Time Plot ",
            fg=self.ACCENT_YELLOW, bg=self.BG_CARD, font=("Arial", 11, "bold"), bd=2
        )
        graph_box.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots(figsize=(4.5, 3.8), facecolor=self.BG_CARD)
        self.ax.set_facecolor("#191A21")
        self.plot_canvas = FigureCanvasTkAgg(self.fig, master=graph_box)
        self.plot_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.status_lbl = tk.Label(
            right_panel, text="Status: Ready for experiment run!",
            font=("Arial", 11, "bold"), fg=self.ACCENT_GREEN, bg=self.BG_CARD,
            pady=8, bd=1, relief=tk.SOLID
        )
        self.status_lbl.pack(fill=tk.X, side=tk.BOTTOM)

        # If files were found initially, trigger auto-selection for the first file
        if self.data_files:
            self.on_file_selected()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TCombobox", fieldbackground="#E0E0E0", background=self.BG_CARD, foreground="black", selectbackground="#BD93F9", selectforeground="black")
        style.map("TCombobox",
                  fieldbackground=[("readonly", "#E0E0E0")],
                  foreground=[("readonly", "black")]  # Ensure text remains black in readonly state
                  )
        self.root.option_add("*TCombobox*Listbox.background", "#E0E0E0")
        self.root.option_add("*TCombobox*Listbox.foreground", "black")
        self.root.option_add("*TCombobox*Listbox.selectBackground", "#BD93F9")
        self.root.option_add("*TCombobox*Listbox.selectForeground", "black")

    def get_available_datasets(self, data_dir="data"):
        """Scans data/ folder and returns a list of JSON files."""
        if os.path.exists(data_dir):
            files = [f for f in os.listdir(data_dir) if f.endswith(".json")]
            return sorted(files)
        return []

    def on_file_selected(self, event=None):
        """Auto-fills Board Size (N) and Seed when a dataset file is selected."""
        selected_file = self.combo_file.get()
        file_path = os.path.join("data", selected_file)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "n" in data:
                self.combo_n.set(data["n"])
            if "seed" in data:
                self.entry_seed.delete(0, tk.END)
                self.entry_seed.insert(0, str(data["seed"]))

    def draw_chessboard(self, canvas, board, n):
        canvas.delete("all")
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        size = min(w, h)
        if size <= 10:
            size = 320

        cell = size / n

        # Render background grid squares
        color_light = "#1E293B"
        color_dark = "#0F172A"

        # Skip grid square outlines for very large N to maintain performance
        if n < 128:
            for r in range(n):
                for c in range(n):
                    color = color_light if (r + c) % 2 == 0 else color_dark
                    canvas.create_rectangle(c * cell, r * cell, (c + 1) * cell, (r + 1) * cell, fill=color, outline="")
        else:
            # Solid background for dense grids
            canvas.create_rectangle(0, 0, size, size, fill=color_dark, outline="")

        # Identify diagonal conflict positions
        conflicts = set()
        for i in range(n):
            for j in range(i + 1, n):
                if abs(i - j) == abs(board[i] - board[j]):
                    conflicts.add(i)
                    conflicts.add(j)

        # Render Queen markers (Dots for N >= 128, Queen symbols ♛ for N < 128)
        for col, row in enumerate(board):
            cx = col * cell + cell / 2
            cy = row * cell + cell / 2
            is_conflict = col in conflicts

            if n >= 128:
                # Small dot rendering for high-density boards
                dot_radius = max(1.0, cell / 2.5)
                dot_color = "#FFD700" if is_conflict else self.ACCENT_YELLOW
                canvas.create_oval(
                    cx - dot_radius, cy - dot_radius,
                    cx + dot_radius, cy + dot_radius,
                    fill=dot_color, outline=""
                )
            else:
                # Standard Unicode Queen Symbol rendering
                q_color = "#FFD700" if is_conflict else self.ACCENT_YELLOW
                font_size = max(10, int(cell * 0.65))
                canvas.create_text(
                    cx, cy,
                    text="♛",
                    fill=q_color,
                    font=("Arial", font_size, "bold")
                )

    def on_run(self):
        try:
            n = int(self.combo_n.get())
            k = int(self.combo_k.get())
            seed = int(self.entry_seed.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid numeric seed or board selection.")
            return

        self.status_lbl.config(text="Executing GA and Wisdom of Crowds algorithms...", fg=self.ACCENT_YELLOW)
        self.root.update()

        ga_res = run_ga(n=n, params={"pop_size": 100, "max_gen": 500}, seed=seed)
        woc_res = run_woc(n=n, crowd_size=k, expert_pct=0.25, seed=seed)

        self.draw_chessboard(self.canvas_ga, ga_res["best_board"], n)
        self.draw_chessboard(self.canvas_woc, woc_res["best_board"], n)

        self.ax.clear()
        self.ax.set_facecolor("#191A21")
        self.ax.plot(ga_res["history"], label=f"GA (Best: {ga_res['best_fitness']})", color=self.ACCENT_PINK,
                     linewidth=2, linestyle="--")
        self.ax.plot(woc_res["history"], label=f"GA+WoC (Best: {woc_res['best_fitness']})", color=self.ACCENT_GREEN,
                     linewidth=2.5)
        self.ax.set_title(f"Fitness Convergence (N={n}, k={k})", color=self.TEXT_COLOR, fontsize=11, fontweight="bold")
        self.ax.set_xlabel("Generations", color=self.ACCENT_CYAN)
        self.ax.set_ylabel("Diagonal Conflicts", color=self.ACCENT_CYAN)
        self.ax.axhline(0, color=self.ACCENT_YELLOW, linestyle=":", alpha=0.7)
        self.ax.tick_params(colors=self.TEXT_COLOR)
        self.ax.legend(facecolor=self.BG_CARD, edgecolor=self.ACCENT_PURPLE)
        self.plot_canvas.draw()

        self.status_lbl.config(
            text=f"Execution Done! | GA Time: {ga_res['runtime_s']:.3f}s | WoC Time: {woc_res['runtime_s']:.3f}s",
            fg=self.ACCENT_GREEN
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = ColorfulNQueensGUI(root)
    root.mainloop()