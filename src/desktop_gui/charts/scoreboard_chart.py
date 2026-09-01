"""
Scoreboard Multi-Line Chart
---------------------------
Displays competitive scoring/activity over time with colored lines and markers.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class ScoreboardChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(10, 5), facecolor="#080404")
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

        # Distinct colors for up to 10 entities/teams
        self.colors = [
            "#3498db", "#e74c3c", "#f1c40f", "#2ecc71", "#9b59b6",
            "#e67e22", "#1abc9c", "#34495e", "#ff6b81", "#7bed9f"
        ]

        self.annot = self.ax.annotate("", xy=(0,0), xytext=(-20,20), textcoords="offset points",
                    bbox=dict(boxstyle="round,pad=0.5", fc="#111118", ec="#2a0a0a", lw=1),
                    arrowprops=dict(arrowstyle="->", color="#c0c0c0"), zorder=100)
        self.annot.set_visible(False)
        self.annot.set_color("#1de9b6")
        self.annot.set_fontfamily("monospace")
        self.annot.set_fontsize(10)
        self.lines = []

        self.canvas.mpl_connect("motion_notify_event", self.hover)
        self.canvas.mpl_connect("button_press_event", self.hover)

    def render_chart(self, teams_data: dict[str, list[dict]]):
        """
        teams_data format:
        {
            "fsociety.0": [{"time": "14:30", "score": 300}, {"time": "15:00", "score": 1200}, ...],
            ...
        }
        """
        self.ax.clear()
        self.lines.clear()
        self.ax.set_facecolor("#080404")

        # Collect all unique time strings for the x-axis properly
        all_times = set()
        for t_list in teams_data.values():
            for point in t_list:
                all_times.add(point["time"])
                
        sorted_times = sorted(list(all_times))
        
        for idx, (team_name, data_points) in enumerate(teams_data.items()):
            color = self.colors[idx % len(self.colors)]
            
            # Map times to their indices so we can plot them correctly
            x_vals = [sorted_times.index(pt["time"]) for pt in data_points]
            y_vals = [pt["score"] for pt in data_points]
            
            line, = self.ax.plot(
                x_vals, y_vals, 
                color=color, 
                marker="o", markersize=6, 
                linewidth=1.5, 
                label=team_name,
                picker=15,
                zorder=2
            )
            self.lines.append((line, team_name))

        self.ax.set_xticks(range(len(sorted_times)))
        self.ax.set_xticklabels(sorted_times, fontsize=9, fontfamily="monospace", color="#888")
        
        self.ax.tick_params(colors="#888", labelsize=9)
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.spines["left"].set_color("#444")
        self.ax.spines["bottom"].set_color("#444")
        
        self.ax.grid(axis='y', linestyle='-', alpha=0.3, color="#444")
        
        self.ax.set_ylim(bottom=0)

        # Legend at the bottom
        legend = self.ax.legend(
            loc='upper center', bbox_to_anchor=(0.5, -0.1),
            ncol=5, frameon=False, prop={'size': 9, 'family': 'monospace'}
        )
        for text in legend.get_texts():
            text.set_color("#c0c0c0")

        self.figure.tight_layout()
        self.canvas.draw()
        
    def hover(self, event):
        vis = self.annot.get_visible()
        if event.inaxes == self.ax:
            for line, name in self.lines:
                cont, ind = line.contains(event)
                if cont:
                    self.update_annot(line, ind, name)
                    self.annot.set_visible(True)
                    self.canvas.draw_idle()
                    return
        if vis:
            self.annot.set_visible(False)
            self.canvas.draw_idle()

    def update_annot(self, line, ind, name):
        x, y = line.get_data()
        x_val = x[ind["ind"][0]]
        y_val = y[ind["ind"][0]]
        self.annot.xy = (x_val, y_val)
        
        # Parse name e.g., "Wallet (bc1e7z)" to "bc1e7z"
        clean_id = name
        if "(" in name and ")" in name:
            clean_id = name.split("(")[1].split(")")[0]
            
        text = f"ID: {clean_id}\nType: Wallet\nRisk: {y_val}"
        self.annot.set_text(text)
        self.annot.get_bbox_patch().set_alpha(0.8)
