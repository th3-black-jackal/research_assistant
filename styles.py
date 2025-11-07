"""
Dark Scientific Theme for Research Assistant
Accent: Electric Blue
Tone: Academic, Precise
"""

DARK_SCIENTIFIC_THEME = """
/* Dark Scientific Theme - Research Assistant */
QMainWindow, QDialog, QWidget {
    background-color: #0a0e14;
    color: #e0e0e0;
    font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
    font-size: 12px;
}

/* Academic Header Styles */
QHeaderView::section {
    background-color: #1a1f29;
    color: #4fc3f7;
    font-weight: bold;
    padding: 8px;
    border: 1px solid #2a3241;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Electric Blue Accents */
QPushButton {
    background-color: #1a1f29;
    color: #e0e0e0;
    border: 1px solid #2a3241;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: 500;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #2a3241;
    border: 1px solid #4fc3f7;
}

QPushButton:pressed {
    background-color: #4fc3f7;
    color: #0a0e14;
}

QPushButton:focus {
    border: 2px solid #4fc3f7;
    outline: none;
}

/* Primary Action Buttons */
QPushButton[class="primary"] {
    background-color: #0066cc;
    color: #ffffff;
    font-weight: bold;
    border: 1px solid #4fc3f7;
}

QPushButton[class="primary"]:hover {
    background-color: #0077e6;
}

QPushButton[class="primary"]:pressed {
    background-color: #0052a3;
}

/* Danger Buttons */
QPushButton[class="danger"] {
    background-color: #c62828;
    color: #ffffff;
    border: 1px solid #f44336;
}

QPushButton[class="danger"]:hover {
    background-color: #d32f2f;
}

/* Tab Widget Styling */
QTabWidget::pane {
    border: 1px solid #2a3241;
    background-color: #0a0e14;
}

QTabWidget::tab-bar {
    alignment: center;
}

QTabBar::tab {
    background-color: #1a1f29;
    color: #b0b0b0;
    padding: 10px 20px;
    margin: 2px;
    border: 1px solid #2a3241;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    font-weight: 500;
}

QTabBar::tab:selected {
    background-color: #2a3241;
    color: #4fc3f7;
    border-bottom: 2px solid #4fc3f7;
    font-weight: bold;
}

QTabBar::tab:hover:!selected {
    background-color: #252b38;
    color: #e0e0e0;
}

/* Group Box Styling */
QGroupBox {
    font-weight: bold;
    color: #4fc3f7;
    border: 1px solid #2a3241;
    border-radius: 6px;
    margin-top: 10px;
    padding-top: 10px;
    background-color: #1a1f29;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 8px;
    background-color: #1a1f29;
    color: #4fc3f7;
    font-weight: bold;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Scientific Progress Bar */
QProgressBar {
    border: 1px solid #2a3241;
    border-radius: 4px;
    background-color: #1a1f29;
    text-align: center;
    color: #e0e0e0;
    font-size: 10px;
}

QProgressBar::chunk {
    background-color: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 #0066cc,
        stop: 0.5 #4fc3f7,
        stop: 1 #0066cc
    );
    border-radius: 3px;
}

/* Text Edit and Display */
QTextEdit, QTextBrowser {
    background-color: #1a1f29;
    color: #e0e0e0;
    border: 1px solid #2a3241;
    border-radius: 4px;
    padding: 8px;
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 11px;
    selection-background-color: #4fc3f7;
    selection-color: #0a0e14;
}

QTextEdit:focus, QTextBrowser:focus {
    border: 1px solid #4fc3f7;
}

/* List Widgets */
QListWidget {
    background-color: #1a1f29;
    color: #e0e0e0;
    border: 1px solid #2a3241;
    border-radius: 4px;
    outline: none;
    font-size: 11px;
}

QListWidget::item {
    padding: 8px;
    border-bottom: 1px solid #2a3241;
    background-color: #1a1f29;
}

QListWidget::item:selected {
    background-color: #4fc3f7;
    color: #0a0e14;
    font-weight: bold;
}

QListWidget::item:hover {
    background-color: #252b38;
}

/* Table Widgets */
QTableWidget {
    background-color: #1a1f29;
    color: #e0e0e0;
    border: 1px solid #2a3241;
    border-radius: 4px;
    gridline-color: #2a3241;
    font-size: 11px;
}

QTableWidget::item {
    padding: 6px;
    border-bottom: 1px solid #2a3241;
    background-color: #1a1f29;
}

QTableWidget::item:selected {
    background-color: #4fc3f7;
    color: #0a0e14;
    font-weight: bold;
}

QTableWidget::item:hover {
    background-color: #252b38;
}

/* Line Edit */
QLineEdit {
    background-color: #1a1f29;
    color: #e0e0e0;
    border: 1px solid #2a3241;
    border-radius: 4px;
    padding: 6px 8px;
    font-size: 11px;
    selection-background-color: #4fc3f7;
    selection-color: #0a0e14;
}

QLineEdit:focus {
    border: 1px solid #4fc3f7;
}

QLineEdit[class="search"] {
    background-color: #252b38;
    border: 1px solid #4fc3f7;
}

/* Combo Box */
QComboBox {
    background-color: #1a1f29;
    color: #e0e0e0;
    border: 1px solid #2a3241;
    border-radius: 4px;
    padding: 6px 8px;
    min-width: 100px;
    font-size: 11px;
}

QComboBox:focus {
    border: 1px solid #4fc3f7;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #4fc3f7;
    width: 0px;
    height: 0px;
}

QComboBox QAbstractItemView {
    background-color: #1a1f29;
    color: #e0e0e0;
    border: 1px solid #2a3241;
    selection-background-color: #4fc3f7;
    selection-color: #0a0e14;
    outline: none;
}

/* Check Box */
QCheckBox {
    color: #e0e0e0;
    spacing: 8px;
    font-size: 11px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #2a3241;
    border-radius: 3px;
    background-color: #1a1f29;
}

QCheckBox::indicator:checked {
    background-color: #4fc3f7;
    border: 1px solid #4fc3f7;
    image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path fill="%230a0e14" d="M13.5 4.5l-7 7-3-3-1.5 1.5 4.5 4.5 8.5-8.5z"/></svg>');
}

QCheckBox::indicator:hover {
    border: 1px solid #4fc3f7;
}

/* Spin Box */
QSpinBox, QDoubleSpinBox {
    background-color: #1a1f29;
    color: #e0e0e0;
    border: 1px solid #2a3241;
    border-radius: 4px;
    padding: 6px 8px;
    font-size: 11px;
    selection-background-color: #4fc3f7;
    selection-color: #0a0e14;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #4fc3f7;
}

QSpinBox::up-button, QDoubleSpinBox::up-button {
    background-color: #2a3241;
    border: 1px solid #2a3241;
    border-top-right-radius: 3px;
    width: 20px;
}

QSpinBox::down-button, QDoubleSpinBox::down-button {
    background-color: #2a3241;
    border: 1px solid #2a3241;
    border-bottom-right-radius: 3px;
    width: 20px;
}

QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-bottom: 5px solid #4fc3f7;
    width: 0px;
    height: 0px;
}

QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #4fc3f7;
    width: 0px;
    height: 0px;
}

/* Scroll Bars */
QScrollBar:vertical {
    background-color: #1a1f29;
    width: 12px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #2a3241;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #4fc3f7;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #1a1f29;
    height: 12px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background-color: #2a3241;
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #4fc3f7;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Splitter */
QSplitter::handle {
    background-color: #2a3241;
    margin: 2px;
}

QSplitter::handle:hover {
    background-color: #4fc3f7;
}

/* Menu Bar */
QMenuBar {
    background-color: #1a1f29;
    color: #e0e0e0;
    border-bottom: 1px solid #2a3241;
    padding: 4px;
}

QMenuBar::item {
    background-color: transparent;
    padding: 6px 12px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background-color: #4fc3f7;
    color: #0a0e14;
}

QMenuBar::item:pressed {
    background-color: #2a3241;
}

/* Menus */
QMenu {
    background-color: #1a1f29;
    color: #e0e0e0;
    border: 1px solid #2a3241;
    border-radius: 4px;
    padding: 4px;
}

QMenu::item {
    padding: 6px 24px 6px 12px;
    border-radius: 3px;
}

QMenu::item:selected {
    background-color: #4fc3f7;
    color: #0a0e14;
}

QMenu::separator {
    height: 1px;
    background-color: #2a3241;
    margin: 4px 8px;
}

/* Status Bar */
QStatusBar {
    background-color: #1a1f29;
    color: #b0b0b0;
    border-top: 1px solid #2a3241;
    padding: 4px;
    font-size: 10px;
}

/* Scientific Labels */
QLabel[class="title"] {
    font-size: 24px;
    font-weight: bold;
    color: #4fc3f7;
    padding: 10px 0px;
}

QLabel[class="subtitle"] {
    font-size: 14px;
    color: #b0b0b0;
    padding: 5px 0px;
}

QLabel[class="accent"] {
    color: #4fc3f7;
    font-weight: bold;
    font-size: 11px;
}

QLabel[class="muted"] {
    color: #808080;
    font-size: 10px;
    font-style: italic;
}

/* Academic Badges and Indicators */
QLabel[class="badge"] {
    background-color: #0066cc;
    color: #ffffff;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 9px;
    font-weight: bold;
}

QLabel[class="indicator"] {
    color: #4fc3f7;
    font-weight: bold;
    font-size: 12px;
}

/* Code and Technical Text */
QLabel[class="code"] {
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    background-color: #252b38;
    color: #4fc3f7;
    padding: 4px 8px;
    border-radius: 3px;
    font-size: 10px;
}

/* Tool Tips */
QToolTip {
    background-color: #1a1f29;
    color: #e0e0e0;
    border: 1px solid #4fc3f7;
    border-radius: 4px;
    padding: 6px;
    font-size: 10px;
}

/* Scientific Visualization Elements */
QFrame[class="separator"] {
    background-color: #2a3241;
    max-height: 1px;
    min-height: 1px;
}

QFrame[class="card"] {
    background-color: #1a1f29;
    border: 1px solid #2a3241;
    border-radius: 6px;
    padding: 12px;
}

/* Analysis Specific Styles */
QProgressBar[class="analysis"] {
    border: 1px solid #4fc3f7;
    background-color: #0a0e14;
}

QProgressBar[class="analysis"]::chunk {
    background-color: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 #0066cc,
        stop: 0.5 #4fc3f7,
        stop: 1 #00bcd4
    );
}

/* GitHub Repository Indicators */
QLabel[class="github-indicator"] {
    color: #00bcd4;
    font-weight: bold;
    font-size: 12px;
}

/* Gap Analysis Impact Levels */
QLabel[class="impact-high"] {
    color: #f44336;
    font-weight: bold;
    background-color: #330000;
    padding: 2px 6px;
    border-radius: 3px;
}

QLabel[class="impact-medium"] {
    color: #ff9800;
    font-weight: bold;
    background-color: #332200;
    padding: 2px 6px;
    border-radius: 3px;
}

QLabel[class="impact-low"] {
    color: #4caf50;
    font-weight: bold;
    background-color: #003300;
    padding: 2px 6px;
    border-radius: 3px;
}
"""