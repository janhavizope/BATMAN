import os
import urllib.request
from PySide6.QtGui import QFontDatabase, QFont
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

FONTS = {
    "Orbitron": "https://github.com/google/fonts/raw/main/ofl/orbitron/Orbitron%5Bwght%5D.ttf",
    "JetBrains Mono": "https://github.com/JetBrains/JetBrainsMono/raw/master/fonts/ttf/JetBrainsMono-Regular.ttf"
}

def setup_theme(app: QApplication):
    # 1. Ensure fonts directory exists
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    fonts_dir = os.path.join(project_root, "resources", "fonts")
    os.makedirs(fonts_dir, exist_ok=True)

    # 2. Download and register fonts
    for font_name, url in FONTS.items():
        font_path = os.path.join(fonts_dir, f"{font_name.replace(' ', '')}.ttf")
        if not os.path.exists(font_path):
            print(f"Downloading {font_name}...")
            try:
                urllib.request.urlretrieve(url, font_path)
            except Exception as e:
                print(f"Failed to download {font_name}: {e}")
        
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id != -1:
                families = QFontDatabase.applicationFontFamilies(font_id)
                if families:
                    print(f"Registered font: {families[0]}")
            else:
                print(f"Failed to register font: {font_path}")

    # 3. Apply Base Font
    app.setFont(QFont("JetBrains Mono", 10))

    # 4. Global QSS (Cyberpunk Hacker Terminal Style - Maroon & Black)
    app.setStyleSheet("""
        /* Deep Dark Background */
        QMainWindow {
            background-color: #080404;
        }
        
        QWidget {
            color: #d4d4d4;
            font-family: 'JetBrains Mono', Consolas, monospace;
        }

        /* Terminal panels (Cards, Sidebar) */
        QFrame.TerminalPanel, QWidget#SidebarWidget {
            background-color: #0d0808;
            border: 1px solid #4a1111;
            border-radius: 6px;
        }

        /* Heading elements */
        QLabel.Heading {
            font-family: 'Orbitron', sans-serif;
            color: #b33939; /* Soft maroon/red */
            font-weight: bold;
            font-size: 15px;
            letter-spacing: 1px;
        }
        
        /* Subtitles / Accents */
        QLabel.Accent {
            color: #9e2a2b; /* Deep muted red */
        }

        /* Buttons */
        QPushButton {
            background-color: #170909;
            border: 1px solid #5e1313;
            color: #e0e0e0;
            font-family: 'Orbitron', sans-serif;
            padding: 6px 14px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #3b0b0b;
            border: 1px solid #b33939;
            color: #ffffff;
        }
        QPushButton:pressed {
            background-color: #5e1313;
            color: #ffffff;
        }
        
        /* Menu Bar */
        QMenuBar {
            background-color: #080404;
            color: #d4d4d4;
            font-family: 'JetBrains Mono', monospace;
            border-bottom: 1px solid #3b0b0b;
        }
        QMenuBar::item {
            background-color: transparent;
            padding: 4px 10px;
        }
        QMenuBar::item:selected {
            background-color: #3b0b0b;
            color: #ffffff;
        }
        
        /* Dropdown Menus */
        QMenu {
            background-color: #0d0808;
            color: #d4d4d4;
            border: 1px solid #4a1111;
            font-family: 'JetBrains Mono', monospace;
        }
        QMenu::item:selected {
            background-color: #5e1313;
            color: #ffffff;
        }
        
        /* Status Bar */
        QStatusBar {
            background-color: #080404;
            color: #a52a2a;
            border-top: 1px solid #3b0b0b;
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
        }
    """)
