"""
Confusion Matrix Chart
----------------------
A PyQt-based widget grid for the confusion matrix.
"""

from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QVBoxLayout
from PySide6.QtCore import Qt

class ConfusionMatrixCard(QWidget):
    def __init__(self, title, count, label_type, bg_color, text_color, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {bg_color}; border-radius: 6px;")
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        count_label = QLabel(str(count))
        count_label.setStyleSheet(f"color: {text_color}; font-weight: bold; font-size: 20px; font-family: Consolas;")
        count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(count_label)
        
        type_label = QLabel(label_type)
        type_label.setStyleSheet(f"color: {text_color}; font-size: 12px; font-family: Consolas;")
        type_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(type_label)


class ConfusionMatrixChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Headers
        h1 = QLabel("Predicted +")
        h1.setStyleSheet("color: #888; font-family: Consolas; font-size: 11px;")
        h1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(h1, 0, 1)
        
        h2 = QLabel("Predicted -")
        h2.setStyleSheet("color: #888; font-family: Consolas; font-size: 11px;")
        h2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(h2, 0, 2)
        
        v1 = QLabel("Actual +")
        v1.setStyleSheet("color: #888; font-family: Consolas; font-size: 11px;")
        v1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(v1, 1, 0)
        
        v2 = QLabel("Actual -")
        v2.setStyleSheet("color: #888; font-family: Consolas; font-size: 11px;")
        v2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(v2, 2, 0)
        
        # Cards (TP, FN, FP, TN)
        self.tp_card = ConfusionMatrixCard("True Positive", 412, "TP", "#1b3a2a", "#1de9b6")
        layout.addWidget(self.tp_card, 1, 1)
        
        self.fn_card = ConfusionMatrixCard("False Negative", 47, "FN", "#4a1c1c", "#e74c3c")
        layout.addWidget(self.fn_card, 1, 2)
        
        self.fp_card = ConfusionMatrixCard("False Positive", 38, "FP", "#4a351c", "#f39c12")
        layout.addWidget(self.fp_card, 2, 1)
        
        self.tn_card = ConfusionMatrixCard("True Negative", 1820, "TN", "#1b3a2a", "#1de9b6")
        layout.addWidget(self.tn_card, 2, 2)
        
        layout.setRowStretch(1, 1)
        layout.setRowStretch(2, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)
