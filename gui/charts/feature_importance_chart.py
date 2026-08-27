"""
Feature Importance Chart
------------------------
Horizontal bar chart using Matplotlib with a vibrant cyan theme.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class FeatureImportanceChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(5, 4), facecolor="#080404")
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

    def render_chart(self, features: list[str], importances: list[float]):
        """Renders a horizontal bar chart of feature importances."""
        self.ax.clear()
        self.ax.set_facecolor("#080404")

        # Sort features by importance ascending so highest is at the top
        sorted_pairs = sorted(zip(features, importances), key=lambda x: x[1])
        f_sorted = [p[0] for p in sorted_pairs]
        i_sorted = [p[1] for p in sorted_pairs]

        # Use vibrant cyan/turquoise (#1de9b6) for the bars
        # Make bars thinner if there are very few features
        bar_height = 0.4 if len(f_sorted) < 3 else 0.6
        bars = self.ax.barh(f_sorted, i_sorted, color="#1de9b6", height=bar_height)

        # X-axis ticks
        self.ax.tick_params(axis='x', colors="#888", labelsize=9)
        self.ax.tick_params(axis='y', colors="#c0c0c0", labelsize=10)
        
        # Grid lines
        self.ax.grid(axis='x', linestyle='--', alpha=0.2, color="#888")
        
        # Hide borders (spines)
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.spines["left"].set_visible(False)
        self.ax.spines["bottom"].set_color("#444")
        
        # Add padding so the labels don't get clipped or overlap external widgets
        self.figure.tight_layout(pad=2.0)
        self.canvas.draw()
