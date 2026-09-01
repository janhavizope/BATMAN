"""
Alerts Page
-----------
Filterable alert table with detail panel.
Cybersecurity dark theme.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QComboBox,
    QLineEdit, QTextEdit,
)
from PySide6.QtGui import QFont

from src.desktop_gui.widgets.dev_badge import DevBadge
from src.desktop_gui.widgets.data_table import DataTable
from src.desktop_gui.data.data_manager import DataManager
from src.desktop_gui.data.filters import filter_alerts
from src.desktop_gui.state.app_state import AppState

_COMBO_STYLE = (
    "QComboBox { background-color: #111118; color: #c0c0c0; border: 1px solid #2a0a0a; "
    "border-radius: 3px; padding: 5px 10px; font-family: Consolas; font-size: 12px; }"
    "QComboBox::drop-down { border: none; }"
    "QComboBox QAbstractItemView { background-color: #111118; color: #c0c0c0; "
    "selection-background-color: #2a0a0a; }"
)
_INPUT_STYLE = (
    "QLineEdit { background-color: #111118; color: #c0c0c0; border: 1px solid #2a0a0a; "
    "border-radius: 3px; padding: 5px 10px; font-family: Consolas; font-size: 12px; }"
)
_DETAIL_STYLE = (
    "QTextEdit { background-color: #111118; color: #c0c0c0; "
    "border: 1px solid #2a0a0a; border-radius: 4px; padding: 8px; "
    "font-family: Consolas; font-size: 12px; }"
)


class AlertsPage(QWidget):
    def __init__(self, app_state: AppState, data_manager: DataManager, parent=None):
        super().__init__(parent)
        self._dm = data_manager
        self._state = app_state

        self.setStyleSheet("background-color: #0a0a0f;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        title = QLabel("ALERTS")
        title.setFont(QFont("Consolas", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #e0e0e0;")
        layout.addWidget(title)
        layout.addWidget(DevBadge())

        # Filters
        filter_row = QHBoxLayout()
        filter_row.setSpacing(12)

        self.level_combo = QComboBox()
        self.level_combo.addItems(["All", "Critical", "High", "Medium", "Low"])
        self.level_combo.setMinimumWidth(150)
        self.level_combo.setStyleSheet(_COMBO_STYLE)

        self.entity_input = QLineEdit()
        self.entity_input.setPlaceholderText("Filter by Entity ID...")
        self.entity_input.setMinimumWidth(220)
        self.entity_input.setStyleSheet(_INPUT_STYLE)

        filter_row.addWidget(QLabel("Level:"))
        filter_row.addWidget(self.level_combo)
        filter_row.addWidget(QLabel("Entity:"))
        filter_row.addWidget(self.entity_input)
        filter_row.addStretch()
        layout.addLayout(filter_row)

        self.level_combo.currentTextChanged.connect(self._on_filter_changed)
        self.entity_input.textChanged.connect(self._on_filter_changed)

        # Table
        self.table = DataTable()
        self.table.selectionModel().selectionChanged.connect(self._on_row_selected)
        layout.addWidget(self.table, stretch=3)

        # Detail panel
        detail_label = QLabel("ALERT DETAIL")
        detail_label.setStyleSheet("color: #6b1a1a; font-family: Consolas; font-size: 11px; font-weight: bold;")
        layout.addWidget(detail_label)

        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setMaximumHeight(130)
        self.detail_text.setStyleSheet(_DETAIL_STYLE)
        layout.addWidget(self.detail_text)

        self._state.entity_selected.connect(self._on_external_entity_selected)

        self.refresh()

    def refresh(self):
        all_alerts = self._dm.get_alerts()
        level = self.level_combo.currentText()
        entity = self.entity_input.text().strip()
        filtered = filter_alerts(all_alerts, risk_level=level, entity_search=entity)
        rows = [a.to_dict() for a in filtered]
        self.table.load_data(rows, columns=["Rank", "Entity ID", "Risk Score", "Risk Level", "Main Reason"])
        self._update_detail(filtered)

    def _on_filter_changed(self):
        self.refresh()

    def _on_row_selected(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return
        row_idx = rows[0].row()
        entity_id = self.table.item(row_idx, 1).text()
        score = self.table.item(row_idx, 2).text()
        level = self.table.item(row_idx, 3).text()
        reason = self.table.item(row_idx, 4).text()
        self._state.selected_alert_entity_id = entity_id
        self.detail_text.setPlainText(
            f"Entity:    {entity_id}\n"
            f"Risk:      {score}/100\n"
            f"Level:     {level}\n"
            f"Reason:    {reason}"
        )

    def _on_external_entity_selected(self, entity_id: str):
        for row_idx in range(self.table.rowCount()):
            item = self.table.item(row_idx, 1)
            if item and item.text() == entity_id:
                self.table.selectRow(row_idx)
                break

    def _update_detail(self, filtered):
        if filtered:
            a = filtered[0]
            self.detail_text.setPlainText(
                f"Entity:    {a.entity_id}\n"
                f"Risk:      {a.risk_score}/100\n"
                f"Level:     {a.risk_level}\n"
                f"Reason:    {a.main_reason}"
            )
        else:
            self.detail_text.setPlainText("No alerts match the current filters.")
