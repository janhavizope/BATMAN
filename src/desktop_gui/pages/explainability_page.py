"""
Explainability Page
-------------------
Anomaly score, top features, evidence, human-readable reasons.
Displays explanation for the currently selected entity.
Cybersecurity dark theme.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QComboBox,
    QSlider, QTextEdit, QPushButton, QGridLayout, QFileDialog,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import csv
import json
import os

from src.desktop_gui.widgets.metric_card import MetricCard
from src.desktop_gui.widgets.dev_badge import DevBadge
from src.desktop_gui.charts.feature_importance_chart import FeatureImportanceChart
from src.desktop_gui.data.data_manager import DataManager
from src.desktop_gui.state.app_state import AppState

_COMBO_STYLE = (
    "QComboBox { background-color: #111118; color: #c0c0c0; border: 1px solid #2a0a0a; "
    "border-radius: 3px; padding: 5px 10px; font-family: Consolas; font-size: 12px; }"
    "QComboBox::drop-down { border: none; }"
    "QComboBox QAbstractItemView { background-color: #111118; color: #c0c0c0; "
    "selection-background-color: #2a0a0a; }"
)
_BTN_STYLE = (
    "QPushButton { background-color: #1a0a0a; color: #6b1a1a; border: 1px solid #2a0a0a; "
    "border-radius: 3px; padding: 6px 14px; font-family: Consolas; font-size: 11px; }"
    "QPushButton:disabled { color: #3a1a1a; }"
)


class ExplainabilityPage(QWidget):
    def __init__(self, app_state: AppState, data_manager: DataManager, parent=None):
        super().__init__(parent)
        self._dm = data_manager
        self._state = app_state

        self.setStyleSheet("background-color: #080404;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        title = QLabel("EXPLAINABILITY")
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

        self.scores_grid = QGridLayout()
        self.scores_grid.setSpacing(10)
        layout.addLayout(self.scores_grid)

        feat_label = QLabel("FEATURE CONTRIBUTIONS")
        feat_label.setStyleSheet("color: #6b1a1a; font-family: Consolas; font-size: 11px; font-weight: bold;")
        layout.addWidget(feat_label)
        
        self.fi_chart = FeatureImportanceChart()
        self.fi_chart.setMinimumHeight(200)
        self.fi_chart.setMaximumHeight(350)
        layout.addWidget(self.fi_chart)

        evidence_label = QLabel("EVIDENCE")
        evidence_label.setStyleSheet("color: #6b1a1a; font-family: Consolas; font-size: 11px; font-weight: bold;")
        layout.addWidget(evidence_label)
        self.evidence_text = QTextEdit()
        self.evidence_text.setReadOnly(True)
        self.evidence_text.setMinimumHeight(60)
        self.evidence_text.setMaximumHeight(100)
        self.evidence_text.setStyleSheet(
            "QTextEdit { background-color: #111118; color: #c0c0c0; "
            "border: 1px solid #2a0a0a; border-radius: 4px; padding: 8px; "
            "font-family: Consolas; font-size: 12px; }"
        )
        layout.addWidget(self.evidence_text)

        reason_label = QLabel("REASON")
        reason_label.setStyleSheet("color: #6b1a1a; font-family: Consolas; font-size: 11px; font-weight: bold;")
        layout.addWidget(reason_label)
        self.reason_text = QTextEdit()
        self.reason_text.setReadOnly(True)
        self.reason_text.setMaximumHeight(100)
        self.reason_text.setStyleSheet(
            "QTextEdit { background-color: #111118; color: #c0c0c0; "
            "border: 1px solid #2a0a0a; border-radius: 4px; padding: 8px; "
            "font-family: Consolas; font-size: 12px; }"
        )
        layout.addWidget(self.reason_text)

        # Threshold
        threshold_row = QHBoxLayout()
        threshold_row.addWidget(QLabel("Threshold:"))
        self.threshold_slider = QSlider(Qt.Orientation.Horizontal)
        self.threshold_slider.setRange(0, 100)
        self.threshold_slider.setValue(50)
        self.threshold_slider.setStyleSheet(
            "QSlider::groove:horizontal { background: #1a0a0a; height: 4px; }"
            "QSlider::handle:horizontal { background: #8b1a1a; width: 14px; margin: -5px 0; border-radius: 7px; }"
        )
        threshold_row.addWidget(self.threshold_slider)
        self.threshold_label = QLabel("0.50")
        self.threshold_label.setStyleSheet("color: #c0c0c0; font-family: Consolas;")
        self.threshold_slider.valueChanged.connect(
            lambda v: self.threshold_label.setText(f"{v/100:.2f}")
        )
        threshold_row.addWidget(self.threshold_label)
        threshold_row.addStretch()
        layout.addLayout(threshold_row)

        # Buttons removed as requested

        self._state.entity_selected.connect(self._on_entity_selected)

        self.refresh()

    def refresh(self):
        entity_ids = self._dm.get_explanation_ids()
        self.entity_combo.blockSignals(True)
        self.entity_combo.clear()
        self.entity_combo.addItems(entity_ids)
        if self._state.selected_entity_id in entity_ids:
            self.entity_combo.setCurrentText(self._state.selected_entity_id)
        self.entity_combo.blockSignals(False)
        eid = self.entity_combo.currentText()
        if eid:
            self._load_explanation(eid)

    def _on_combo_changed(self, text: str):
        if text:
            self._state.selected_entity_id = text
            self._load_explanation(text)

    def _on_entity_selected(self, entity_id: str):
        self.entity_combo.blockSignals(True)
        idx = self.entity_combo.findText(entity_id)
        if idx >= 0:
            self.entity_combo.setCurrentIndex(idx)
        self.entity_combo.blockSignals(False)
        self._load_explanation(entity_id)

    def _load_explanation(self, entity_id: str):
        expl = self._dm.get_explanation(entity_id)
        if expl is None:
            return
        
        self._clear_layout(self.scores_grid)
        self.scores_grid.addWidget(MetricCard("ANOMALY SCORE", f"{expl.anomaly_score:.2f}"), 0, 0)
        self.scores_grid.addWidget(MetricCard("RISK SCORE", f"{expl.risk_score}/100"), 0, 1)

        features = [f["feature"] for f in expl.top_features]
        importances = [f["contribution"] for f in expl.top_features]
        self.fi_chart.render_chart(features, importances)

        self.evidence_text.setPlainText(
            "\n".join(f"  {i+1}. {ev}" for i, ev in enumerate(expl.evidence))
        )
        self.reason_text.setPlainText(expl.human_reason)

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def _export_csv(self):
        """Export current explanation to CSV file."""
        entity_id = self.entity_combo.currentText()
        if not entity_id:
            return
        
        expl = self._dm.get_explanation(entity_id)
        if expl is None:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Explanation as CSV",
            f"{entity_id}_explanation.csv",
            "CSV Files (*.csv)",
            options=QFileDialog.DontUseNativeDialog
        )
        
        if file_path:
            if not file_path.endswith('.csv'):
                file_path += '.csv'
            try:
                with open(file_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Entity ID", entity_id])
                    writer.writerow(["Anomaly Score", f"{expl.anomaly_score:.4f}"])
                    writer.writerow(["Risk Score", expl.risk_score])
                    writer.writerow([])
                    writer.writerow(["Feature", "Contribution", "Direction"])
                    for feat in expl.top_features:
                        writer.writerow([
                            feat.get("feature", ""),
                            f"{feat.get('contribution', 0):.4f}",
                            feat.get("direction", "")
                        ])
                    writer.writerow([])
                    writer.writerow(["Evidence"])
                    for evidence in expl.evidence:
                        writer.writerow([evidence])
                    writer.writerow([])
                    writer.writerow(["Explanation"])
                    writer.writerow([expl.human_reason])
            except Exception as e:
                print(f"Error exporting CSV: {e}")

    def _export_shap(self):
        """Export SHAP/feature importance data to JSON."""
        entity_id = self.entity_combo.currentText()
        if not entity_id:
            return
        
        expl = self._dm.get_explanation(entity_id)
        if expl is None:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export SHAP Values",
            f"{entity_id}_shap.json",
            "JSON Files (*.json)",
            options=QFileDialog.DontUseNativeDialog
        )
        
        if file_path:
            if not file_path.endswith('.json'):
                file_path += '.json'
            try:
                shap_data = {
                    "entity_id": entity_id,
                    "anomaly_score": float(expl.anomaly_score),
                    "risk_score": int(expl.risk_score),
                    "top_features": expl.top_features,
                    "evidence": expl.evidence,
                    "explanation": expl.human_reason
                }
                
                with open(file_path, 'w') as f:
                    json.dump(shap_data, f, indent=2)
            except Exception as e:
                print(f"Error exporting SHAP: {e}")

    def _export_pdf(self):
        """Export explanation as PDF report."""
        entity_id = self.entity_combo.currentText()
        if not entity_id:
            return
        
        expl = self._dm.get_explanation(entity_id)
        if expl is None:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export PDF Report",
            f"{entity_id}_report.pdf",
            "PDF Files (*.pdf)",
            options=QFileDialog.DontUseNativeDialog
        )
        
        if file_path:
            if not file_path.endswith('.pdf'):
                file_path += '.pdf'
            try:
                # For now, save as text-based report (can be enhanced with actual PDF library)
                report_content = f"""
BATMAN - EXPLAINABILITY REPORT
================================

Entity ID: {entity_id}
Anomaly Score: {expl.anomaly_score:.4f}
Risk Score: {expl.risk_score}/100

TOP CONTRIBUTING FEATURES:
"""
                for i, feat in enumerate(expl.top_features, 1):
                    report_content += f"\n{i}. {feat.get('feature', '')} - Contribution: {feat.get('contribution', 0):.4f} ({feat.get('direction', '')})"
                
                report_content += "\n\nEVIDENCE:\n"
                for i, evidence in enumerate(expl.evidence, 1):
                    report_content += f"\n{i}. {evidence}"
                
                report_content += f"\n\nHUMAN EXPLANATION:\n{expl.human_reason}\n"
                
                # Save as PDF (basic text-to-PDF, or could use reportlab for advanced features)
                with open(file_path, 'w') as f:
                    f.write(report_content)
            except Exception as e:
                print(f"Error exporting PDF: {e}")
