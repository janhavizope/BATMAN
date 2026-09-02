"""
Overview Charts
---------------
matplotlib-based charts for the Overview dashboard.
Cybersecurity dark theme.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout

from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure
import matplotlib.ticker as ticker


import numpy as np
from scipy.interpolate import make_interp_spline

class SeverityDistributionDonut(QWidget):
    """Donut chart showing severity distribution matching the reference."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(5, 3), facecolor="#0a0a0f")
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)
        
        self.annot = self.ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                    bbox=dict(boxstyle="round,pad=0.5", fc="#111118", ec="#2a0a0a", lw=1),
                    arrowprops=dict(arrowstyle="->", color="#c0c0c0"))
        self.annot.set_visible(False)
        self.annot.set_color("#1de9b6")
        self.annot.set_fontfamily("monospace")
        self.canvas.mpl_connect("motion_notify_event", self.hover)

    def render_chart(self, data: dict[str, int]):
        self.ax.clear()
        self.ax.set_facecolor("#0a0a0f")

        labels = ["Critical", "High", "Medium", "Low"]
        values = [data.get(l, 0) for l in labels]
        colors = ["#f2353c", "#f39c12", "#3498db", "#2ecc71"]

        plot_vals = [v for v in values if v > 0]
        plot_colors = [c for v, c in zip(values, colors) if v > 0]
        self.plot_labels = [l for v, l in zip(values, labels) if v > 0]
        
        if not plot_vals:
            plot_vals = [1]
            plot_colors = ["#333333"]
            self.plot_labels = ["No Data"]

        self.wedges, _ = self.ax.pie(
            plot_vals, 
            colors=plot_colors, 
            startangle=90, 
            wedgeprops=dict(width=0.4, edgecolor="#0a0a0f", linewidth=2)
        )
        self.plot_vals = plot_vals

        # Add a legend so it's not "blank with no clue"
        self.ax.legend(
            self.wedges, 
            self.plot_labels, 
            loc="center left", 
            bbox_to_anchor=(0.9, 0, 0.5, 1),
            frameon=False,
            labelcolor="#c0c0c0",
            fontsize=10
        )

        self.figure.tight_layout()
        self.canvas.draw()
        
    def hover(self, event):
        if event.inaxes == self.ax:
            for i, wedge in enumerate(self.wedges):
                if wedge.contains_point([event.x, event.y]):
                    total = sum(self.plot_vals)
                    val = self.plot_vals[i]
                    pct = (val / total) * 100 if total > 0 else 0
                    label = self.plot_labels[i]
                    
                    self.annot.xy = (event.xdata, event.ydata)
                    self.annot.set_text(f"{label}\n{val} ({pct:.1f}%)")
                    self.annot.set_visible(True)
                    self.canvas.draw_idle()
                    return
        self.annot.set_visible(False)
        self.canvas.draw_idle()


class ActivityTimelineChart(QWidget):
    """Smoothed line/area chart matching the 'Alerts over time (7d)' reference."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(5, 3), facecolor="#0a0a0f")
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)
        
        self.annot = self.ax.annotate("", xy=(0,0), xytext=(-20,20), textcoords="offset points",
                    bbox=dict(boxstyle="round,pad=0.5", fc="#111118", ec="#2a0a0a", lw=1),
                    arrowprops=dict(arrowstyle="->", color="#c0c0c0"))
        self.annot.set_visible(False)
        self.annot.set_color("#1de9b6")
        self.annot.set_fontfamily("monospace")
        self.canvas.mpl_connect("motion_notify_event", self.hover)

    def render_chart(self, timestamps: list[str], counts: list[int]):
        self.ax.clear()
        self.ax.set_facecolor("#0a0a0f")

        if len(timestamps) > 1:
            x = np.arange(len(timestamps))
            y = np.array(counts)

            x_smooth = np.linspace(x.min(), x.max(), 300)
            spline = make_interp_spline(x, y, k=min(3, len(x)-1))
            y_smooth = spline(x_smooth)
            y_smooth = np.clip(y_smooth, 0, None)

            self.ax.plot(x_smooth, y_smooth, color="#21d093", linewidth=2.5)
            self.ax.fill_between(x_smooth, y_smooth, alpha=0.1, color="#21d093")

            self.points, = self.ax.plot(x, y, "o", color="#21d093", markersize=5, markerfacecolor="#21d093", markeredgecolor="#0a0a0f", markeredgewidth=1)
            self.timestamps = timestamps
            self.counts = counts
        else:
            x = range(len(timestamps))
            self.points, = self.ax.plot(x, counts, color="#21d093", linewidth=2.5, marker="o")
            self.timestamps = timestamps
            self.counts = counts

        self.ax.grid(True, linestyle="--", linewidth=0.5, color="#2a3b45", alpha=0.5)

        short_labels = [t.split(" ")[-1][:5] if " " in t else t[:5] for t in timestamps]
        step = max(1, len(short_labels) // 6)
        self.ax.set_xticks(range(0, len(short_labels), step))
        self.ax.set_xticklabels(short_labels[::step], fontsize=9, fontfamily="monospace", color="#888")

        self.ax.tick_params(colors="#888", labelsize=9)
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.spines["bottom"].set_color("#2a3b45")
        self.ax.spines["left"].set_color("#2a3b45")
        self.ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

        self.figure.tight_layout()
        self.canvas.draw()
        
    def hover(self, event):
        if event.inaxes == self.ax and hasattr(self, 'points'):
            cont, ind = self.points.contains(event)
            if cont:
                idx = ind["ind"][0]
                t = self.timestamps[idx]
                c = self.counts[idx]
                
                self.annot.xy = (event.xdata, event.ydata)
                self.annot.set_text(f"{t}\nAlerts: {c}")
                self.annot.set_visible(True)
                self.canvas.draw_idle()
                return
        if self.annot.get_visible():
            self.annot.set_visible(False)
            self.canvas.draw_idle()
