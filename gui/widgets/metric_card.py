"""
Metric Card Widget
------------------
A QFrame displaying a label and a large value, used for KPI grids.
Cybersecurity aesthetic: dark background, maroon accent border.
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class MetricCard(QFrame):
    def __init__(self, label: str, value: str, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setProperty("class", "TerminalPanel")
        
        # We can add a custom hover effect using QSS directly on this class in theme_setup or inline here
        self.setStyleSheet("""
            MetricCard {
                background-color: rgba(13, 5, 5, 220);
                border: 1px solid #8b0000;
                border-radius: 8px;
            }
            MetricCard:hover {
                background-color: rgba(40, 10, 10, 240);
                border: 1px solid #ff3333;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)

        lbl = QLabel(label)
        lbl.setStyleSheet("color: #ff4d4d; font-size: 11px; font-family: 'JetBrains Mono', monospace; font-weight: bold;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignLeft)

        val = QLabel(value)
        val.setObjectName("metricValue")
        val.setStyleSheet("color: #e0e0e0; font-size: 26px; font-weight: bold; font-family: 'Orbitron', sans-serif;")
        val.setAlignment(Qt.AlignmentFlag.AlignLeft)

        layout.addWidget(lbl)
        layout.addWidget(val)
