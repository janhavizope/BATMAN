"""
Network Graph Page
------------------
Interactive graph with controls, filters, and stats.
Cybersecurity dark theme.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QComboBox,
    QSlider, QCheckBox, QGridLayout, QTableWidget, QTableWidgetItem,
    QHeaderView,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from src.desktop_gui.widgets.dev_badge import DevBadge
from src.desktop_gui.widgets.metric_card import MetricCard
from src.desktop_gui.graph.graph_view import GraphView
from src.desktop_gui.data.data_manager import DataManager
from src.desktop_gui.data.filters import filter_graph_nodes
from src.desktop_gui.state.app_state import AppState

_COMBO_STYLE = (
    "QComboBox { background-color: #111118; color: #c0c0c0; border: 1px solid #2a0a0a; "
    "border-radius: 3px; padding: 5px 10px; font-family: Consolas; font-size: 12px; }"
    "QComboBox::drop-down { border: none; }"
    "QComboBox QAbstractItemView { background-color: #111118; color: #c0c0c0; "
    "selection-background-color: #2a0a0a; }"
)
_CHECK_STYLE = (
    "QCheckBox { color: #c0c0c0; font-family: Consolas; font-size: 11px; }"
    "QCheckBox::indicator { border: 1px solid #2a0a0a; background-color: #111118; }"
    "QCheckBox::indicator:checked { background-color: #8b1a1a; border-color: #8b1a1a; }"
)
_SLIDER_STYLE = (
    "QSlider::groove:horizontal { background: #1a0a0a; height: 4px; }"
    "QSlider::handle:horizontal { background: #8b1a1a; width: 14px; margin: -5px 0; border-radius: 7px; }"
)
_TABLE_STYLE = (
    "QTableWidget { background-color: #0f0f14; alternate-background-color: #141419; "
    "color: #c0c0c0; border: 1px solid #2a0a0a; font-family: Consolas; font-size: 11px; }"
    "QHeaderView::section { background-color: #1a0a0a; color: #8b1a1a; padding: 6px; "
    "border: 1px solid #2a0a0a; font-weight: bold; font-family: Consolas; }"
)


class NetworkGraphPage(QWidget):
    def __init__(self, app_state: AppState, data_manager: DataManager, parent=None):
        super().__init__(parent)
        self._dm = data_manager
        self._state = app_state

        self.setStyleSheet("background-color: #080404;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # Title
        title_row = QHBoxLayout()
        title = QLabel("Network Traffic Analysis")
        title.setFont(QFont("Consolas", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff;")
        title_row.addWidget(title)
        title_row.addStretch()
        title_row.addWidget(DevBadge())
        layout.addLayout(title_row)
        
        # Subtitle
        subtitle = QLabel("Top 10 Anomalous Entities")
        subtitle.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
        subtitle.setStyleSheet("color: #888888;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        # Export Buttons Row
        from PySide6.QtWidgets import QPushButton
        btn_style = (
            "QPushButton { background-color: #1a0a0a; color: #c0c0c0; border: 1px solid #8b1a1a; "
            "border-radius: 3px; padding: 5px 15px; font-family: Consolas; font-weight: bold; }"
            "QPushButton:hover { background-color: #2a0a0a; border-color: #1de9b6; color: #1de9b6; }"
        )
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.btn_csv = QPushButton("Download .csv")
        self.btn_csv.setStyleSheet(btn_style)
        self.btn_html = QPushButton("View HTML")
        self.btn_html.setStyleSheet(btn_style)
        btn_row.addWidget(self.btn_csv)
        btn_row.addWidget(self.btn_html)
        layout.addLayout(btn_row)

        self.btn_csv.clicked.connect(self._download_csv)
        self.btn_html.clicked.connect(self._view_html)

        # The Scoreboard Chart
        from src.desktop_gui.charts.scoreboard_chart import ScoreboardChart
        self.chart = ScoreboardChart()
        self.chart.setMinimumHeight(400)
        layout.addWidget(self.chart, stretch=2)

        # The Ranking Table
        from src.desktop_gui.widgets.data_table import DataTable
        self.table = DataTable()
        layout.addWidget(self.table, stretch=1)

        self.refresh()

    def refresh(self):
        # Fetch scoreboard data
        scoreboard_data = self._dm.get_scoreboard()
        
        # 1. Render the multi-line chart
        self.chart.render_chart(scoreboard_data)
        
        # 2. Build the ranking table
        final_scores = []
        for team, points in scoreboard_data.items():
            if points:
                last_score = points[-1]["score"]
                final_scores.append({"Team": team, "Score": last_score})
                
        # Sort descending by score
        final_scores.sort(key=lambda x: x["Score"], reverse=True)
        
        # Create row dicts with Place
        table_rows = []
        for idx, item in enumerate(final_scores):
            table_rows.append({
                "Rank": idx + 1,
                "Entity ID": item["Team"],
                "Risk Score": item["Score"]
            })
            
        self.table.load_data(table_rows, columns=["Rank", "Entity ID", "Risk Score"])

    def _download_csv(self):
        import csv
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        
        path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)", options=QFileDialog.DontUseNativeDialog)
        if not path:
            return
        if not path.endswith('.csv'):
            path += '.csv'
            
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Rank", "Entity ID", "Risk Score"])
                for row in range(self.table.rowCount()):
                    r = self.table.item(row, 0).text()
                    e = self.table.item(row, 1).text()
                    s = self.table.item(row, 2).text()
                    writer.writerow([r, e, s])
            QMessageBox.information(self, "Success", f"Successfully exported records to CSV.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save CSV: {e}")

    def _view_html(self):
        import tempfile
        import webbrowser
        import os
        
        html = [
            "<html><head><style>",
            "body { font-family: Consolas, monospace; background: #0a0a0f; color: #c0c0c0; padding: 20px; }",
            "table { border-collapse: collapse; width: 100%; margin-top: 20px; }",
            "th, td { border: 1px solid #2a0a0a; padding: 8px; text-align: left; }",
            "th { background-color: #1a0a0a; color: #8b1a1a; font-weight: bold; }",
            "tr:nth-child(even) { background-color: #141419; }",
            "h2 { color: #1de9b6; }",
            "</style></head><body>",
            "<h2>Top 10 Anomalous Entities</h2>",
            "<table>",
            "<tr><th>Rank</th><th>Entity ID</th><th>Risk Score</th></tr>"
        ]
        
        for row in range(self.table.rowCount()):
            r = self.table.item(row, 0).text()
            e = self.table.item(row, 1).text()
            s = self.table.item(row, 2).text()
            html.append(f"<tr><td>{r}</td><td>{e}</td><td>{s}</td></tr>")
            
        html.append("</table></body></html>")
        
        try:
            fd, path = tempfile.mkstemp(suffix=".html", prefix="batman_top10_")
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write("\n".join(html))
            webbrowser.open(f"file://{os.path.abspath(path)}")
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to generate HTML report: {e}")
