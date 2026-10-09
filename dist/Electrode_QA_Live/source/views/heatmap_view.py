"""Responsive electrode circles with scrolling and click-to-inspect."""
import math
import tkinter as tk
from tkinter import ttk
from config import COLORS, COLOR_LABELS


def grid_positions(count, columns):
    return [(i//max(1, columns), i % max(1, columns)) for i in range(count)]


class HeatmapView(ttk.Frame):
    def __init__(self, parent, on_select):
        super().__init__(parent)
        self.on_select, self.electrodes, self.mode = on_select, [], "current"
        self.canvas = tk.Canvas(self, bg="#F4F7FA", highlightthickness=0)
        scroll = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda _: self.draw())
        self.canvas.bind("<MouseWheel>", lambda e: self.canvas.yview_scroll(-int(e.delta/120), "units"))

    def show(self, electrodes, mode):
        self.electrodes, self.mode = electrodes, mode
        self.draw()

    def draw(self):
        canvas = self.canvas
        canvas.delete("all")
        width = max(240, canvas.winfo_width())
        if not self.electrodes:
            canvas.create_text(width/2, 100, text="Choose BDF records and channels\nClick Run analysis", fill="#6B7A89", font=("Segoe UI", 15), justify="center")
            canvas.configure(scrollregion=(0, 0, width, 200))
            return
        columns = max(1, min(len(self.electrodes), int(width/120)))
        cell = width/columns
        for i, (row, col) in enumerate(grid_positions(len(self.electrodes), columns)):
            item = self.electrodes[i]
            metric = item.metric(self.mode)
            cx, cy, radius = cell*(col+.5), 58+row*128, min(42, cell*.34)
            tag = f"electrode-{i}"
            canvas.create_oval(cx-radius, cy-radius, cx+radius, cy+radius, fill=COLORS.get(metric.color, '#929EAA'),
                               outline="white", width=3, tags=(tag, "electrode_circle"))
            text_color = "#243243" if metric.color == "yellow" else "white"
            canvas.create_text(cx, cy-7, text=item.name, fill=text_color, font=("Segoe UI", 12, "bold"), tags=tag)
            canvas.create_text(cx, cy+16, text="REF" if item.is_reference else str(i+1), fill=text_color, font=("Segoe UI", 9), tags=tag)
            canvas.create_text(cx, cy+radius+14, text={"green":"Within limits", "yellow":"Review", "red":"Check"}.get(metric.color, 'Not assessed'),
                               fill="#46566A", font=("Segoe UI", 10), tags=tag)
            canvas.tag_bind(tag, "<Button-1>", lambda _, electrode=item: self.on_select(electrode))
            canvas.tag_bind(tag, "<Enter>", lambda _: canvas.configure(cursor="hand2"))
            canvas.tag_bind(tag, "<Leave>", lambda _: canvas.configure(cursor=""))
        canvas.configure(scrollregion=(0, 0, width, math.ceil(len(self.electrodes)/columns)*128+10))


class HeatmapRenderer:
    """Export the same electrode statuses without needing a Tk window."""
    def save(self, electrodes, mode, path, title="Electrode QA"):
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_agg import FigureCanvasAgg
        from matplotlib.patches import Circle, Patch
        from matplotlib import font_manager
        installed = {f.name for f in font_manager.fontManager.ttflist}
        font = next((f for f in ("Segoe UI", "Arial", "DejaVu Sans") if f in installed), "DejaVu Sans")
        n = len(electrodes)
        columns = min(12, max(1, math.ceil(math.sqrt(n*1.5))))
        rows = math.ceil(n/columns)
        fig = Figure(figsize=(max(7, columns*1.45), max(4.2, rows*1.5+1.8)), facecolor="#F4F7FA", layout="constrained")
        FigureCanvasAgg(fig)
        ax = fig.add_subplot()
        ax.set_aspect("equal")
        ax.set(xlim=(-.55, columns-.45), ylim=(rows-.4, -.65))
        ax.axis("off")
        for i, (row, col) in enumerate(grid_positions(n, columns)):
            item = electrodes[i]
            color = item.metric(mode).color
            ax.add_patch(Circle((col, row), .34, facecolor=COLORS[color], edgecolor="white", lw=2))
            text_color = "#243243" if color == "yellow" else "white"
            ax.text(col, row-.04, item.name, ha="center", va="center", color=text_color, weight="bold", fontsize=11, fontfamily=font)
            ax.text(col, row+.16, "REF" if item.is_reference else str(i+1), ha="center", va="center", color=text_color, fontsize=8)
            ax.text(col, row+.48, {"green":"Within limits", "yellow":"Review", "red":"Check"}[color], ha="center", va="center", color="#46566A", fontsize=10, fontfamily=font)
        fig.suptitle(f"{title}\n{n} electrodes · {mode}", fontsize=16, fontfamily=font, color="#243243")
        fig.legend(handles=[Patch(color=c, label=COLOR_LABELS[k]) for k, c in COLORS.items()], loc="outside lower center",
                   ncol=3, prop={"family":font, "size":10}, frameon=False)
        fig.savefig(path, dpi=170)
