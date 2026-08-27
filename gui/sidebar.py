"""
Sidebar Navigation
------------------
QListWidget-based sidebar with cybersecurity aesthetic.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QFrame
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont


class Sidebar(QWidget):
    page_changed = Signal(int)

    NAV_ITEMS = [
        "Overview",
        "Transaction Analysis",
        "Network Graph",
        "Entity Investigation",
        "Alerts",
        "Explainability",
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SidebarWidget")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 16, 12, 16)

        title = QLabel("BATMAN")
        title.setStyleSheet("color: #d4d4d4; font-size: 32px; font-weight: bold; font-family: 'Orbitron', sans-serif;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("BITCOIN ANOMALY TRAFFIC AND\nMONITORING ANALYSIS NETWORK")
        subtitle.setStyleSheet("color: #c06c6c; font-size: 10px; font-weight: bold; font-family: 'Orbitron', sans-serif;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #8b0000;")
        layout.addWidget(line)

        self.list_widget = QListWidget()
        self.list_widget.setObjectName("NavList")
        self.list_widget.setStyleSheet(
            "QListWidget {"
            "  background-color: transparent;"
            "  border: none;"
            "  font-size: 13px;"
            "  font-family: 'Orbitron', sans-serif;"
            "}"
            "QListWidget::item {"
            "  padding: 12px 10px;"
            "  margin-bottom: 4px;"
            "  border-radius: 4px;"
            "  color: #a0a0a0;"
            "  border-left: 3px solid transparent;"
            "}"
            "QListWidget::item:selected {"
            "  background-color: rgba(94, 19, 19, 0.4);"
            "  color: #d4d4d4;"
            "  border-left: 3px solid #b33939;"
            "}"
            "QListWidget::item:hover {"
            "  background-color: rgba(40, 10, 10, 0.8);"
            "  color: #c06c6c;"
            "}"
        )
        for name in self.NAV_ITEMS:
            item = QListWidgetItem(f"> {name}")
            self.list_widget.addItem(item)
        self.list_widget.setCurrentRow(0)
        layout.addWidget(self.list_widget)

        self.list_widget.currentRowChanged.connect(self.page_changed.emit)

        layout.addStretch()

        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setStyleSheet("color: #8b0000;")
        layout.addWidget(line2)

        footer = QLabel("BITCOIN\nANALYSIS ENGINE")
        footer.setStyleSheet("color: #c06c6c; font-size: 12px; font-weight: bold; font-family: 'Orbitron', sans-serif;")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer)
