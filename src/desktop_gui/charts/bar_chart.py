"""
Bar Chart Widget
----------------
Horizontal bar chart with cybersecurity dark theme.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QStyledItemDelegate,
)
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QColor


class _BarDelegate(QStyledItemDelegate):
    """Paints a horizontal colour bar inside each cell of the Contribution column."""

    def __init__(self, parent=None, colour="#8b1a1a"):
        super().__init__(parent)
        self.colour = colour

    def paint(self, painter: QPainter, option, index):
        painter.save()
        painter.fillRect(option.rect, QColor("#0f0f14"))
        value = index.data(Qt.ItemDataRole.UserRole) or 0.0
        bar_rect = QRect(option.rect)
        bar_rect.setWidth(int(bar_rect.width() * value))
        painter.fillRect(bar_rect, QColor(self.colour))
        painter.setPen(QColor("#e0e0e0"))
        painter.drawText(option.rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                         f"  {value:.2f}")
        painter.restore()


class BarChart(QWidget):
    """Renders a horizontal bar chart from a list of (label, value) pairs."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Feature", "Contribution"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(1, 180)
        self.table.setItemDelegateForColumn(1, _BarDelegate(self.table))
        self.table.setStyleSheet(
            "QTableWidget {"
            "  background-color: #0f0f14;"
            "  color: #c0c0c0;"
            "  border: 1px solid #2a0a0a;"
            "  border-radius: 4px;"
            "  font-size: 12px;"
            "  font-family: Consolas;"
            "}"
            "QHeaderView::section {"
            "  background-color: #1a0a0a;"
            "  color: #8b1a1a;"
            "  padding: 6px;"
            "  border: 1px solid #2a0a0a;"
            "  font-weight: bold;"
            "  font-family: Consolas;"
            "}"
        )
        layout.addWidget(self.table)

    def load_data(self, items: list[tuple[str, float]]):
        """items = [(label, value), ...]"""
        self.table.setRowCount(len(items))
        for r, (label, value) in enumerate(items):
            label_item = QTableWidgetItem(label)
            label_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(r, 0, label_item)

            val_item = QTableWidgetItem()
            val_item.setData(Qt.ItemDataRole.UserRole, value)
            self.table.setItem(r, 1, val_item)
