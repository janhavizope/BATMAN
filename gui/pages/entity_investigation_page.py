"""
Entity Investigation Page
-------------------------
Display entity profile, timeline, network, evidence, features, explanation.
Cybersecurity dark theme.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QComboBox,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QTextEdit, QFrame, QGridLayout,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from gui.widgets.metric_card import MetricCard
from gui.widgets.dev_badge import DevBadge
from gui.data.data_manager import DataManager
from gui.state.app_state import AppState

_COMBO_STYLE = (
    "QComboBox { background-color: #111118; color: #c0c0c0; border: 1px solid #2a0a0a; "
    "border-radius: 3px; padding: 5px 10px; font-family: Consolas; font-size: 12px; }"
    "QComboBox::drop-down { border: none; }"
    "QComboBox QAbstractItemView { background-color: #111118; color: #c0c0c0; "
    "selection-background-color: #2a0a0a; }"
)
_TAB_STYLE = (
    "QTabWidget::pane { border: 1px solid #2a0a0a; background-color: #0a0a0f; }"
    "QTabBar::tab { background-color: #111118; color: #888; padding: 8px 16px; "
    "border: 1px solid #2a0a0a; border-bottom: none; font-family: Consolas; font-size: 11px; }"
    "QTabBar::tab:selected { background-color: #1a0a0a; color: #e0e0e0; "
    "border-bottom: 2px solid #8b1a1a; }"
)
_TABLE_STYLE = (
    "QTableWidget { background-color: #0f0f14; alternate-background-color: #141419; "
    "color: #c0c0c0; border: 1px solid #2a0a0a; font-family: Consolas; font-size: 12px; }"
    "QHeaderView::section { background-color: #1a0a0a; color: #8b1a1a; padding: 6px; "
    "border: 1px solid #2a0a0a; font-weight: bold; font-family: Consolas; }"
)
_TEXT_STYLE = (
    "QTextEdit { background-color: #111118; color: #c0c0c0; "
    "border: 1px solid #2a0a0a; border-radius: 4px; padding: 8px; "
    "font-family: Consolas; font-size: 12px; }"
)


class EntityInvestigationPage(QWidget):
    def __init__(self, app_state: AppState, data_manager: DataManager, parent=None):
        super().__init__(parent)
        self._dm = data_manager
        self._state = app_state
        self._current_entity_id = ""

        self.setStyleSheet("background-color: #0a0a0f;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        title = QLabel("ENTITY INVESTIGATION")
        title.setFont(QFont("Consolas", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #e0e0e0;")
        layout.addWidget(title)
        layout.addWidget(DevBadge())

        sel_row = QHBoxLayout()
        sel_row.addWidget(QLabel("Entity:"))
        self.entity_combo = QComboBox()
        self.entity_combo.setMinimumWidth(200)
        self.entity_combo.setStyleSheet(_COMBO_STYLE)
        self.entity_combo.currentTextChanged.connect(self._on_combo_changed)
        sel_row.addWidget(self.entity_combo)
        sel_row.addStretch()
        layout.addLayout(sel_row)

        self.card_layout = QGridLayout()
        self.card_layout.setSpacing(10)
        self.cards_frame = QFrame()
        self.cards_frame.setLayout(self.card_layout)
        layout.addWidget(self.cards_frame)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(_TAB_STYLE)
        layout.addWidget(self.tabs, stretch=1)

        self._build_timeline_tab()
        self._build_network_tab()
        self._build_evidence_tab()
        self._build_features_tab()
        self._build_explanation_tab()
        self._build_notes_tab()

        self._state.entity_selected.connect(self._on_entity_selected)

        self.refresh()

    def refresh(self):
        entity_ids = self._dm.get_entity_ids()
        self.entity_combo.blockSignals(True)
        self.entity_combo.clear()
        self.entity_combo.addItems(entity_ids)
        if self._state.selected_entity_id in entity_ids:
            self.entity_combo.setCurrentText(self._state.selected_entity_id)
        self.entity_combo.blockSignals(False)
        eid = self.entity_combo.currentText()
        if eid:
            self._load_entity(eid)

    def _on_combo_changed(self, text: str):
        if text:
            self._state.selected_entity_id = text
            self._load_entity(text)

    def _on_entity_selected(self, entity_id: str):
        self.entity_combo.blockSignals(True)
        idx = self.entity_combo.findText(entity_id)
        if idx >= 0:
            self.entity_combo.setCurrentIndex(idx)
        self.entity_combo.blockSignals(False)
        self._load_entity(entity_id)

    def _load_entity(self, entity_id: str):
        entity = self._dm.get_entity(entity_id)
        if entity is None:
            return
        self._clear_layout(self.card_layout)
        card_data = [
            ("ENTITY ID", entity.entity_id),
            ("RISK SCORE", f"{entity.risk_score}/100"),
            ("RISK LEVEL", entity.risk_level),
            ("ANOMALY SCORE", f"{entity.anomaly_score:.2f}"),
            ("TRANSACTIONS", str(entity.transaction_count)),
            ("COUNTERPARTIES", str(entity.counterparty_count)),
        ]
        for idx, (label, value) in enumerate(card_data):
            self.card_layout.addWidget(MetricCard(label, value), idx // 3, idx % 3)

        self.timeline_table.setRowCount(len(entity.timeline))
        for r, ev in enumerate(entity.timeline):
            self.timeline_table.setItem(r, 0, QTableWidgetItem(ev.get("timestamp", "")))
            self.timeline_table.setItem(r, 1, QTableWidgetItem(ev.get("event", "")))

        self.network_table.setRowCount(len(entity.network_associations))
        for r, assoc in enumerate(entity.network_associations):
            self.network_table.setItem(r, 0, QTableWidgetItem(assoc.get("type", "")))
            self.network_table.setItem(r, 1, QTableWidgetItem(assoc.get("value", "")))

        self.evidence_text.setPlainText("\n".join(
            f"  {i+1}. {ev}" for i, ev in enumerate(entity.evidence)
        ))

        self.features_table.setRowCount(len(entity.top_features))
        for r, feat in enumerate(entity.top_features):
            self.features_table.setItem(r, 0, QTableWidgetItem(feat.get("feature", "")))
            self.features_table.setItem(r, 1, QTableWidgetItem(f"{feat.get('contribution', 0):.2f}"))

        self.explanation_text.setPlainText(entity.explanation)
        self._current_entity_id = entity_id

    def _build_timeline_tab(self):
        self.timeline_table = QTableWidget()
        self.timeline_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.timeline_table.verticalHeader().setVisible(False)
        self.timeline_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.timeline_table.setColumnCount(2)
        self.timeline_table.setHorizontalHeaderLabels(["Timestamp", "Event"])
        self.timeline_table.setStyleSheet(_TABLE_STYLE)
        self.tabs.addTab(self.timeline_table, "Timeline")

    def _build_network_tab(self):
        self.network_table = QTableWidget()
        self.network_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.network_table.verticalHeader().setVisible(False)
        self.network_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.network_table.setColumnCount(2)
        self.network_table.setHorizontalHeaderLabels(["Type", "Value"])
        self.network_table.setStyleSheet(_TABLE_STYLE)
        self.tabs.addTab(self.network_table, "Network")

    def _build_evidence_tab(self):
        self.evidence_text = QTextEdit()
        self.evidence_text.setReadOnly(True)
        self.evidence_text.setStyleSheet(_TEXT_STYLE)
        self.tabs.addTab(self.evidence_text, "Evidence")

    def _build_features_tab(self):
        self.features_table = QTableWidget()
        self.features_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.features_table.verticalHeader().setVisible(False)
        self.features_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.features_table.setColumnCount(2)
        self.features_table.setHorizontalHeaderLabels(["Feature", "Contribution"])
        self.features_table.setStyleSheet(_TABLE_STYLE)
        self.tabs.addTab(self.features_table, "Features")

    def _build_explanation_tab(self):
        self.explanation_text = QTextEdit()
        self.explanation_text.setReadOnly(True)
        self.explanation_text.setStyleSheet(_TEXT_STYLE)
        self.tabs.addTab(self.explanation_text, "Explanation")

    def _build_notes_tab(self):
        notes_layout = QVBoxLayout()
        self.notes_text = QTextEdit()
        self.notes_text.setPlaceholderText("Investigation notes...")
        self.notes_text.setStyleSheet(_TEXT_STYLE)
        notes_layout.addWidget(self.notes_text)
        container = QWidget()
        container.setLayout(notes_layout)
        self.tabs.addTab(container, "Notes")

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
