from pathlib import Path
from typing import List, Dict, Any, Optional

from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt, Slot, QObject
from PySide6.QtWidgets import QApplication, QStyle  # <--- ADDED IMPORTS

from utils.logger import setup_logger

logger = setup_logger(__name__)

class ProjectTreeModel(QStandardItemModel):
    """
    A specialized model to handle file system hierarchy with recursive 
    tri-state checkbox logic.
    """
    
    # Custom role to store the absolute Path object within the item
    PATH_ROLE = Qt.UserRole + 1

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.root_path: Optional[Path] = None
        # Connect the internal signal to our robust handler
        self.itemChanged.connect(self.on_item_changed)

    def populate(self, scan_data: Dict[str, Any], root_path: Path):
        """
        Populates the model from the scanner's dictionary output.
        
        Args:
            scan_data: Nested dictionary from FileScanner.
            root_path: The absolute path of the project root.
        """
        self.clear()
        self.setHorizontalHeaderLabels(["Project Files"])
        self.root_path = root_path

        root_item = self.invisibleRootItem()
        self._build_tree_recursive(scan_data, root_item, root_path)

    def _build_tree_recursive(self, data: Dict[str, Any], parent_item: QStandardItem, current_path: Path):
        """
        Recursively creates QStandardItems from the dictionary.
        Sorts items so folders appear before files.
        """
        # Sort: Directories first, then files, both alphabetically
        sorted_keys = sorted(data.keys(), key=lambda k: (data[k] is None, k.lower()))

        for name in sorted_keys:
            child_path = current_path / name
            item_data = data[name]
            
            item = QStandardItem(name)
            item.setCheckable(True)
            item.setEditable(False)
            item.setData(child_path, self.PATH_ROLE)
            item.setCheckState(Qt.Unchecked)

            if item_data is not None:
                # It is a directory
                # FIX: Access style via QApplication instance
                icon = QApplication.style().standardIcon(QStyle.SP_DirIcon)
                item.setIcon(icon)
                
                self._build_tree_recursive(item_data, item, child_path)
            else:
                # It is a file
                # Optional: You could add SP_FileIcon here if desired
                # icon = QApplication.style().standardIcon(QStyle.SP_FileIcon)
                # item.setIcon(icon)
                pass 

            parent_item.appendRow(item)

    def get_checked_files(self) -> List[Path]:
        """
        Returns a list of Path objects for all leaf nodes (files) that are Checked.
        """
        checked_files = []
        
        # Stack-based traversal to avoid recursion limits on deep trees
        stack = [self.invisibleRootItem()]
        while stack:
            parent = stack.pop()
            for row in range(parent.rowCount()):
                child = parent.child(row)
                if child.hasChildren():
                    stack.append(child)
                else:
                    # It's a file
                    if child.checkState() == Qt.Checked:
                        path = child.data(self.PATH_ROLE)
                        if path:
                            checked_files.append(path)
        return checked_files

    @Slot(QStandardItem)
    def on_item_changed(self, item: QStandardItem):
        """
        Handles check state changes. 
        1. Propagates state DOWN to children (if any).
        2. Propagates state UP to parents (calculating partials).
        """
        # CRITICAL: Block signals to prevent infinite recursion loops 
        # while we programmatically update other items.
        self.blockSignals(True)
        try:
            new_state = item.checkState()
            
            # 1. Downward Propagation (if folder)
            if item.hasChildren():
                self._set_children_state(item, new_state)

            # 2. Upward Propagation
            self._update_parent_state(item)
            
        except Exception as e:
            logger.error(f"Error during tree state update: {e}")
        finally:
            self.blockSignals(False)
            
        # Manually emit layoutChanged or dataChanged if View doesn't repaint
        # Usually implicitly handled by the checkState change, but explicitly 
        # signaling the model has changed is good practice if UI lags.
        # self.layoutChanged.emit() 

    def _set_children_state(self, parent: QStandardItem, state: Qt.CheckState):
        """Recursively sets all children to the specific state."""
        # If parent is PartiallyChecked, we usually treat user click as Unchecking or Checking all.
        # Here we assume the input 'state' is the target state.
        for row in range(parent.rowCount()):
            child = parent.child(row)
            child.setCheckState(state)
            if child.hasChildren():
                self._set_children_state(child, state)

    def _update_parent_state(self, item: QStandardItem):
        """
        Traverses up the tree, recalculating parent states based on siblings.
        """
        parent = item.parent()
        if parent is None:
            return

        child_count = parent.rowCount()
        checked_count = 0
        partial_count = 0

        for row in range(child_count):
            child = parent.child(row)
            state = child.checkState()
            if state == Qt.Checked:
                checked_count += 1
            elif state == Qt.PartiallyChecked:
                partial_count += 1

        new_parent_state = Qt.Unchecked
        
        if checked_count == child_count:
            new_parent_state = Qt.Checked
        elif checked_count > 0 or partial_count > 0:
            new_parent_state = Qt.PartiallyChecked
        
        if parent.checkState() != new_parent_state:
            parent.setCheckState(new_parent_state)
            # Continue recursion up
            self._update_parent_state(parent)
