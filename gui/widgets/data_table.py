"""
Data Table Widget
-----------------
QTableWidget wrapper with cybersecurity dark theme.
"""

from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Qt


class DataTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.setStyleSheet(
            "QTableWidget {"
            "  background-color: rgba(13, 8, 8, 200);"
            "  alternate-background-color: rgba(20, 10, 10, 200);"
            "  color: #c0c0c0;"
            "  gridline-color: #2a1111;"
            "  border: 1px solid #4a1111;"
            "  border-radius: 4px;"
            "  font-size: 13px;"
            "  font-family: 'JetBrains Mono', monospace;"
            "}"
            "QTableWidget::item:hover {"
            "  background-color: rgba(40, 15, 15, 220);"
            "  color: #c06c6c;"
            "}"
            "QTableWidget::item:selected {"
            "  background-color: #5e1313;"
            "  color: #ffffff;"
            "}"
            "QHeaderView::section {"
            "  background-color: rgba(15, 8, 8, 240);"
            "  color: #b33939;"
            "  padding: 6px;"
            "  border: 1px solid #2a1111;"
            "  border-bottom: 2px solid #5e1313;"
            "  font-weight: bold;"
            "  font-family: 'Orbitron', sans-serif;"
            "  font-size: 12px;"
            "}"
        )

    def load_data(self, rows: list[dict], columns: list[str] | None = None):
        """Populate the table from a list of dicts."""
        if not rows:
            self.setRowCount(0)
            self.setColumnCount(0)
            return

        if columns is None:
            columns = list(rows[0].keys())

        self.setColumnCount(len(columns))
        self.setHorizontalHeaderLabels(columns)
        self.setRowCount(len(rows))

        from PySide6.QtGui import QBrush, QColor
        for row_idx, row_data in enumerate(rows):
            for col_idx, col_name in enumerate(columns):
                val = row_data.get(col_name, "")
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                
                # Apply text colors to match screenshot capsules
                if str(val) == "Critical":
                    item.setForeground(QBrush(QColor("#f2353c")))
                elif str(val) == "High":
                    item.setForeground(QBrush(QColor("#f39c12")))
                elif str(val) == "Medium":
                    item.setForeground(QBrush(QColor("#3498db")))
                elif str(val) == "Low":
                    item.setForeground(QBrush(QColor("#2ecc71")))
                elif str(val) == "Open":
                    item.setForeground(QBrush(QColor("#95a5a6")))
                elif str(val) == "Closed":
                    item.setForeground(QBrush(QColor("#7f8c8d")))
                
                self.setItem(row_idx, col_idx, item)
