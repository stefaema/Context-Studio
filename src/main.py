import sys
import os
import argparse
import logging
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox, QFileDialog
from PySide6.QtGui import QPalette, QColor, QFont
from PySide6.QtCore import Qt

from view.main_window import MainWindow
from controller.app_controller import AppController
from utils.logger import setup_logger

# Initialize logger
logger = setup_logger("root")

# ... [Keep set_dark_theme and global_exception_hook unchanged] ...
def set_dark_theme(app: QApplication):
    # (Same as previous version)
    app.setStyle("Fusion")
    font = QFont("Segoe UI", 11)
    app.setFont(font)
    dark_palette = QPalette()
    # ... (Same palette code) ...
    dark_palette.setColor(QPalette.Window, QColor(45, 45, 45))
    dark_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Base, QColor(55, 55, 55))
    dark_palette.setColor(QPalette.AlternateBase, QColor(45, 45, 45))
    dark_palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Text, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Button, QColor(45, 45, 45))
    dark_palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(100, 100, 100))
    dark_palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(dark_palette)

def global_exception_hook(exctype, value, traceback):
    logger.critical("Unhandled exception occurred", exc_info=(exctype, value, traceback))
    app = QApplication.instance()
    if app:
        error_msg = f"An unexpected error occurred:\n{value}\n\nCheck the log file for details."
        QMessageBox.critical(None, "Critical Error", error_msg)
    sys.__excepthook__(exctype, value, traceback)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Context Studio: LLM Context Manager")
    # Default is None, so we know if user provided it or not
    parser.add_argument("path", nargs="?", default=None, help="Path to project")
    return parser.parse_args()

def main():
    sys.excepthook = global_exception_hook
    args = parse_arguments()
    
    app = QApplication(sys.argv)
    app.setApplicationName("Context Studio")
    set_dark_theme(app)

    try:
        # 1. Initialize GUI and Controller
        main_window = MainWindow()
        controller = AppController(view=main_window)
        
        # 2. Determine Initial Path
        initial_path = None

        if args.path:
            # Case A: Path provided via CLI
            initial_path = str(Path(args.path).resolve())
        else:
            # Case B: No path -> Open File Explorer
            # We use QFileDialog directly here before showing the main window,
            # or we show the main window and then the dialog. 
            # Showing dialog before window can feel like a "splash" setup.
            initial_path = QFileDialog.getExistingDirectory(None, "Select Project Root", os.getcwd())
            
            if not initial_path:
                # User cancelled the dialog at startup -> Exit app?
                # Or just open empty? Let's exit as per "choose first" logic.
                sys.exit(0)

        # 3. Load Project
        controller.load_project(initial_path)
        
        # 4. Show Window
        main_window.show()
        sys.exit(app.exec())

    except Exception as e:
        logger.critical(f"Failed to initialize application: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
