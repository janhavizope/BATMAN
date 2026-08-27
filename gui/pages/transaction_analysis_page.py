"""
Transaction Analysis Page
-------------------------
Transaction table, detail view, filters.
Cybersecurity dark theme.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QComboBox,
    QLineEdit, QTextEdit, QGridLayout, QFrame,
)
from PySide6.QtGui import QFont

from gui.widgets.metric_card import MetricCard
from gui.widgets.dev_badge import DevBadge
from gui.widgets.data_table import DataTable
from gui.graph.graph_view import GraphView
from gui.data.data_manager import DataManager
from gui.data.filters import filter_transactions
from gui.state.app_state import AppState

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


class TransactionAnalysisPage(QWidget):
    def __init__(self, app_state: AppState, data_manager: DataManager, parent=None):
        super().__init__(parent)
        self._dm = data_manager
        self._state = app_state

        self.setStyleSheet("background-color: #0a0a0f;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        title = QLabel("TRANSACTION ANALYSIS")
        title.setFont(QFont("Consolas", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #e0e0e0;")
        layout.addWidget(title)
        layout.addWidget(DevBadge())

        # High-Level Attack Graph Embedded
        self.graph_view = GraphView()
        self.graph_view.setMinimumHeight(300)
        layout.addWidget(self.graph_view, stretch=3)

        # Data Table Below Graph
        self.table = DataTable()
        self.table.selectionModel().selectionChanged.connect(self._on_row_selected)
        layout.addWidget(self.table, stretch=2)

        # Detail cards
        self.detail_grid = QGridLayout()
        self.detail_grid.setSpacing(10)
        self.detail_frame = QFrame()
        self.detail_frame.setLayout(self.detail_grid)
        layout.addWidget(self.detail_frame)

        # Extended details
        self.ext_text = QTextEdit()
        self.ext_text.setReadOnly(True)
        self.ext_text.setMaximumHeight(80)
        self.ext_text.setStyleSheet(_DETAIL_STYLE)
        layout.addWidget(self.ext_text)

        # Filters and Exports
        from PySide6.QtWidgets import QPushButton
        filter_row = QHBoxLayout()
        filter_row.setSpacing(12)
        self.flag_combo = QComboBox()
        self.flag_combo.addItems(["All Flags", "Suspicious", "Normal"])
        self.flag_combo.setStyleSheet(_COMBO_STYLE)
        self.min_amount_input = QLineEdit()
        self.min_amount_input.setPlaceholderText("Min Amount (BTC)")
        self.min_amount_input.setMaximumWidth(160)
        self.min_amount_input.setStyleSheet(_INPUT_STYLE)
        
        btn_style = (
            "QPushButton { background-color: #1a0a0a; color: #c0c0c0; border: 1px solid #8b1a1a; "
            "border-radius: 3px; padding: 5px 15px; font-family: Consolas; font-weight: bold; }"
            "QPushButton:hover { background-color: #2a0a0a; border-color: #1de9b6; color: #1de9b6; }"
        )
        self.btn_clear_filter = QPushButton("Clear Entity Filter")
        self.btn_clear_filter.setStyleSheet(btn_style)
        self.btn_csv = QPushButton("Download .csv")
        self.btn_csv.setStyleSheet(btn_style)
        self.btn_html = QPushButton("View HTML")
        self.btn_html.setStyleSheet(btn_style)

        filter_row.addWidget(QLabel("Flag:"))
        filter_row.addWidget(self.flag_combo)
        filter_row.addWidget(self.min_amount_input)
        filter_row.addWidget(self.btn_clear_filter)
        filter_row.addStretch()
        filter_row.addWidget(self.btn_csv)
        filter_row.addWidget(self.btn_html)
        layout.addLayout(filter_row)

        self.flag_combo.currentTextChanged.connect(self._on_filter_changed)
        self.min_amount_input.textChanged.connect(self._on_filter_changed)
        self.btn_clear_filter.clicked.connect(self._clear_entity_filter)
        self.btn_csv.clicked.connect(self._download_csv)
        self.btn_html.clicked.connect(self._view_html)

        self._state.entity_selected.connect(self._on_entity_selected)

        self.refresh()

    def refresh(self):
        all_txns = self._dm.get_transactions()
        entity_filter = self._state.selected_entity_id or None
        
        if entity_filter:
            self.btn_clear_filter.setText(f"Clear Filter: {entity_filter[:8]}...")
            self.btn_clear_filter.show()
        else:
            self.btn_clear_filter.hide()

        flag = self.flag_combo.currentText()
        min_amt_text = self.min_amount_input.text().strip()
        min_amt = float(min_amt_text) if min_amt_text else None
        filtered = filter_transactions(all_txns, entity_id=entity_filter, flag=flag, min_amount=min_amt)
        rows = [t.to_dict() for t in filtered]
        self.table.load_data(rows, columns=["Transaction ID", "Amount (BTC)", "Timestamp",
                                             "Source", "Destination", "Flag"])
        
        # Render the high-level graph
        graph_data = self._dm.get_graph()
        self.graph_view.render_graph(
            nodes=[n.to_dict() for n in graph_data.nodes], 
            edges=[e.to_dict() for e in graph_data.edges], 
            highlight_entity=entity_filter
        )

    def _clear_entity_filter(self):
        self._state.selected_entity_id = ""
        self.refresh()

    def _on_filter_changed(self):
        self.refresh()

    def _on_entity_selected(self, entity_id: str):
        self.refresh()

    def _on_row_selected(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return
        row_idx = rows[0].row()
        detail = {
            "transaction_id": self.table.item(row_idx, 0).text(),
            "amount_btc": float(self.table.item(row_idx, 1).text()),
            "timestamp": self.table.item(row_idx, 2).text(),
            "source": self.table.item(row_idx, 3).text(),
            "destination": self.table.item(row_idx, 4).text(),
            "flag": self.table.item(row_idx, 5).text(),
        }
        self._show_detail(detail)

    def _show_detail(self, d: dict):
        self._clear_layout(self.detail_grid)
        card_data = [
            ("TX ID", str(d.get("transaction_id", "—"))),
            ("AMOUNT", f"{d.get('amount_btc', 0):.4f} BTC"),
            ("TIMESTAMP", d.get("timestamp", "—")),
            ("SOURCE", d.get("source", "—")),
            ("DESTINATION", d.get("destination", "—")),
            ("FLAG", d.get("flag", "—")),
        ]
        for idx, (label, value) in enumerate(card_data):
            self.detail_grid.addWidget(MetricCard(label, value), idx // 3, idx % 3)
        self.ext_text.setPlainText(
            f"Source:      {d.get('source', '—')}\n"
            f"Destination: {d.get('destination', '—')}\n"
            f"Flag:        {d.get('flag', '—')}"
        )

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def _get_current_filtered_data(self):
        all_txns = self._dm.get_transactions()
        entity_filter = self._state.selected_entity_id or None
        flag = self.flag_combo.currentText()
        min_amt_text = self.min_amount_input.text().strip()
        min_amt = float(min_amt_text) if min_amt_text else None
        return filter_transactions(all_txns, entity_id=entity_filter, flag=flag, min_amount=min_amt)

    def _download_csv(self):
        import csv
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        
        path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
        if not path:
            return
            
        filtered = self._get_current_filtered_data()
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Transaction ID", "Amount (BTC)", "Timestamp", "Source", "Destination", "Flag"])
                for t in filtered:
                    writer.writerow([t.tx_id, t.amount_btc, t.timestamp, t.source, t.destination, t.flag])
            QMessageBox.information(self, "Success", f"Successfully exported {len(filtered)} records to CSV.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save CSV: {e}")

    def _view_html(self):
        import tempfile
        import webbrowser
        import os
        
        filtered = self._get_current_filtered_data()
        html = [
            "<html><head><style>",
            "body { font-family: Consolas, monospace; background: #0a0a0f; color: #c0c0c0; padding: 20px; }",
            "table { border-collapse: collapse; width: 100%; margin-top: 20px; }",
            "th, td { border: 1px solid #2a0a0a; padding: 8px; text-align: left; }",
            "th { background-color: #1a0a0a; color: #8b1a1a; font-weight: bold; }",
            "tr:nth-child(even) { background-color: #141419; }",
            "h2 { color: #1de9b6; }",
            "</style></head><body>",
            "<h2>Transaction Analysis Report</h2>",
            "<table>",
            "<tr><th>Transaction ID</th><th>Amount (BTC)</th><th>Timestamp</th><th>Source</th><th>Destination</th><th>Flag</th></tr>"
        ]
        
        for t in filtered:
            html.append(f"<tr><td>{t.tx_id}</td><td>{t.amount_btc}</td><td>{t.timestamp}</td><td>{t.source}</td><td>{t.destination}</td><td>{t.flag}</td></tr>")
            
        html.append("</table></body></html>")
        
        try:
            fd, path = tempfile.mkstemp(suffix=".html", prefix="batman_report_")
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write("\n".join(html))
            webbrowser.open(f"file://{os.path.abspath(path)}")
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to generate HTML report: {e}")
