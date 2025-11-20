from pathlib import Path
from typing import Callable, Any, Optional

from PySide6.QtWidgets import QMessageBox

from model.file_scanner import FileScanner
from model.context_builder import ContextBuilder
from model.project_tree_model import ProjectTreeModel
from utils.clipboard_service import ClipboardService
from utils.logger import setup_logger

# Type hinting for the View
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from view.main_window import MainWindow

logger = setup_logger(__name__)

class AppController:
    """
    Orchestrates the interaction between the Model and View.
    """

    def __init__(self, view: 'MainWindow'):
        self.view = view
        self.root_path: Optional[Path] = None
        
        # Initialize core components (stateless or empty)
        self.tree_model = ProjectTreeModel()
        self.builder = ContextBuilder()
        self.scanner: Optional[FileScanner] = None
        
        # Connect View Signals
        self.view.copy_button.clicked.connect(self.copy_context_to_clipboard)
        self.view.open_button.clicked.connect(self.select_root_folder)
        
        # Connect Model Signals
        self.tree_model.itemChanged.connect(self._on_tree_selection_changed)

        # Initial setup of view model (empty state)
        self.view.set_tree_model(self.tree_model)

    def load_project(self, root_path: str):
        """
        Loads a new project into the application.
        """
        logger.info(f"Loading project: {root_path}")
        try:
            path_obj = Path(root_path).resolve()
            if not path_obj.exists() or not path_obj.is_dir():
                raise ValueError(f"Invalid directory: {root_path}")
            
            self.root_path = path_obj
            
            # Re-initialize scanner with new path
            self.scanner = FileScanner(
                self.root_path, 
                excluded_dirs=[".git", "__pycache__", "venv", "node_modules", ".idea", ".vscode"]
            )
            
            # Perform Scan
            scan_data = self.scanner.scan()
            
            # Populate Model
            self.tree_model.populate(scan_data, self.root_path)
            
            # Reset Preview
            self.view.update_preview("")
            self.view.update_status_bar(0, 0)
            
            # Update Window Title
            self.view.setWindowTitle(f"Context Studio - {self.root_path.name}")

        except Exception as e:
            logger.error(f"Failed to load project: {e}", exc_info=True)
            self.view.show_error("Load Failed", f"Could not load project:\n{e}")

    def select_root_folder(self):
        """
        Opens the directory picker and loads the selected project.
        """
        selected_dir = self.view.prompt_directory_selection()
        if selected_dir:
            self._safe_execute(lambda: self.load_project(selected_dir))

    def _on_tree_selection_changed(self, _item):
        """Triggered whenever the user checks/unchecks a file."""
        if not self.root_path:
            return
        self._safe_execute(self._regenerate_preview)

    def _regenerate_preview(self):
        selected_files = self.tree_model.get_checked_files()
        context_str = self.builder.build_context_string(selected_files, self.root_path)
        token_count = self.builder.estimate_token_count(context_str)
        
        self.view.update_preview(context_str)
        self.view.update_status_bar(token_count, len(selected_files))

    def copy_context_to_clipboard(self):
        text = self.view.get_preview_text()
        success, msg = ClipboardService.copy_text(text)
        if success:
            self.view.show_status_message(msg, duration=3000)
        else:
            self.view.show_error("Copy Failed", msg)

    def _safe_execute(self, func: Callable[[], Any]):
        try:
            func()
        except Exception as e:
            logger.error(f"Error executing {func.__name__}: {e}", exc_info=True)
            self.view.show_error("Application Error", f"An unexpected error occurred: {e}")
