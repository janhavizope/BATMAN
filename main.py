"""
BATMAN — Bitcoin Anomaly Traffic & Monitoring Analysis Network
==============================================================

Entry point for the PySide6 desktop application.

Run with:
    python main.py
"""

import sys
import os

# Ensure project root is on the path so gui.* and backend.* resolve.
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from src.desktop_gui.main_window import MainWindow
from src.desktop_gui.utils.theme_setup import setup_theme

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("BATMAN")
    app.setApplicationDisplayName("BATMAN — Bitcoin Transaction Traffic Monitor")
    
    # Set base style to Fusion before applying our custom theme
    app.setStyle("Fusion")
    
    # Apply our new cyberpunk hacker theme
    setup_theme(app)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
