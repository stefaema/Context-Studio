from typing import Optional
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTreeView, QTextEdit, QSplitter, QPushButton, 
    QMessageBox, QAbstractItemView, QFileDialog
)
from PySide6.QtGui import QFontDatabase
from PySide6.QtCore import Qt, QAbstractItemModel

from .status_bar import TokenStatusBar

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Context Studio")
        self.resize(1200, 850) # Slightly taller

        # -- Components --
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(12, 12, 12, 12) 
        self.main_layout.setSpacing(12)

        # Header / Toolbar Area
        self.header_layout = QHBoxLayout()
        self.copy_button = QPushButton("COPY CONTEXT TO CLIPBOARD")
        self.copy_button.setCursor(Qt.PointingHandCursor)
        self.copy_button.setMinimumHeight(45)

        # Open Project Button
        self.open_button = QPushButton("OPEN PROJECT")
        self.open_button.setCursor(Qt.PointingHandCursor)
        self.open_button.setMinimumHeight(45)
        self.open_button.setStyleSheet("""
            QPushButton {
                background-color: #3d3d3d;
                color: white;
                font-weight: bold;
                font-size: 11pt;
                border: 1px solid #555;
                border-radius: 6px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
                border-color: #666;
            }
        """)

        # Modern Button Styling
        self.copy_button.setStyleSheet("""
            QPushButton {
                background-color: #0078D7;
                color: white;
                font-weight: bold;
                font-size: 11pt;
                border: none;
                border-radius: 6px;
                padding: 5px;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background-color: #0063B1;
            }
            QPushButton:pressed {
                background-color: #004C87;
            }
        """)
        self.header_layout.addWidget(self.open_button)
        self.header_layout.addWidget(self.copy_button)
        self.main_layout.addLayout(self.header_layout)

        # 2. Splitter Area (Tree + Preview)
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setHandleWidth(2) 
        
        # -- LEFT: Tree View --
        self.tree_view = QTreeView()
        self.tree_view.setSelectionMode(QAbstractItemView.NoSelection)
        self.tree_view.setAnimated(True)
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setIndentation(20)
        
        self.tree_view.setStyleSheet("""
            QTreeView {
                background-color: #2b2b2b;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                font-size: 11pt;
            }
            QTreeView::item {
                padding: 4px; /* More spacing between items */
                color: #e0e0e0;
            }
            QTreeView::item:hover {
                background-color: #3d3d3d; /* Subtle dark grey hover, NOT blue */
                border-radius: 2px;
            }
            QTreeView::item:selected {
                background-color: #4d4d4d; /* Neutral selection color */
            }
            /* Fix Checkbox contrast against dark background */
            QTreeView::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #666;
                background-color: #333;
                border-radius: 3px;
            }
            QTreeView::indicator:checked {
                background-color: #0078D7; /* Blue accent only on the active checkbox */
                border: 1px solid #0078D7;
                image: none; /* Use default check, or provide custom SVG if needed */
            }
            QTreeView::indicator:unchecked:hover {
                border: 1px solid #888;
            }
        """)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlaceholderText("Select files to generate context...")
        
        # Code Font
        fixed_font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        fixed_font.setPointSize(11) # Ramped up size
        self.preview_text.setFont(fixed_font)
        
        # Style the Preview Box
        self.preview_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 5px;
            }
        """)

        self.splitter.addWidget(self.tree_view)
        self.splitter.addWidget(self.preview_text)
        
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 2) # Code area wider

        self.main_layout.addWidget(self.splitter)

        # 3. Status Bar
        self.status_bar = TokenStatusBar()
        self.setStatusBar(self.status_bar)

    # -- Public Interface --

    def prompt_directory_selection(self) -> Optional[str]:
        """Opens a dialog for the user to select a directory."""
        return QFileDialog.getExistingDirectory(self, "Select Project Root")
    
    def set_tree_model(self, model: QAbstractItemModel):
        self.tree_view.setModel(model)
        self.tree_view.expandToDepth(0)

    def update_preview(self, text: str):
        self.preview_text.setPlainText(text)

    def get_preview_text(self) -> str:
        return self.preview_text.toPlainText()

    def update_status_bar(self, token_count: int, file_count: int):
        self.status_bar.update_metrics(token_count, file_count)

    def show_error(self, title: str, message: str):
        QMessageBox.critical(self, title, message)

    def show_status_message(self, message: str, duration: int = 3000):
        self.status_bar.showMessage(message, duration)
