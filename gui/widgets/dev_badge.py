"""
Dev Badge Widget
----------------
Cybersecurity-style warning banner for development/placeholder data.
"""

from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt


class DevBadge(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText(
            "  [LIVE MODE] ML MODEL CONNECTED  "
            "— Data is being populated by the trained Random Forest inferences."
        )
        self.setStyleSheet(
            "QLabel {"
            "  background-color: #0a1a0a;"
            "  border: 1px solid #153a15;"
            "  border-left: 3px solid #1a8b1a;"
            "  border-radius: 3px;"
            "  padding: 8px 14px;"
            "  font-size: 11px;"
            "  font-family: Consolas;"
            "  color: #1a8b1a;"
            "}"
        )
        self.setWordWrap(True)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
