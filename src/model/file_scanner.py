import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from utils.logger import setup_logger

logger = setup_logger(__name__)

class FileScanner:
    """
    Robust file system scanner responsible for recursively traversing directories
    while filtering noise and handling file system errors gracefully.
    """

    def __init__(self, root_path: Path, excluded_dirs: Optional[List[str]] = None):
        """
        Initialize the scanner.

        Args:
            root_path: The absolute path to the directory to scan.
            excluded_dirs: A list of directory names to ignore.
        
        Raises:
            ValueError: If root_path does not exist or is not a directory.
        """
        self.root_path = root_path.resolve()
        self.excluded_dirs = set(excluded_dirs) if excluded_dirs else set()
        
        # Defensive check for root existence
        if not self.root_path.exists():
            logger.error(f"Root path does not exist: {self.root_path}")
            raise ValueError(f"Path does not exist: {self.root_path}")
        if not self.root_path.is_dir():
            logger.error(f"Root path is not a directory: {self.root_path}")
            raise ValueError(f"Path is not a directory: {self.root_path}")

    def scan(self) -> Dict[str, Any]:
        """
        Performs the scan starting from the root path.

        Returns:
            Dict[str, Any]: A nested dictionary structure representing the file tree.
                            Files are represented by None, Directories by a Dict.
        """
        logger.info(f"Starting scan at {self.root_path}")
        visited_inodes: Set[int] = set()  # To prevent symlink recursion loops
        
        try:
            return self._recursive_scan(self.root_path, visited_inodes)
        except Exception as e:
            logger.critical(f"Fatal error during directory scan: {e}", exc_info=True)
            return {}

    def _recursive_scan(self, current_path: Path, visited_inodes: Set[int]) -> Dict[str, Any]:
        """
        Internal recursive method to scan a directory.
        
        Args:
            current_path: The path currently being scanned.
            visited_inodes: Set of file system inodes visited to detect loops.

        Returns:
            Dict representation of the current directory.
        """
        tree_structure: Dict[str, Any] = {}

        # Symlink Loop Protection (Linux/Unix specific mostly, but good practice)
        try:
            stat_info = current_path.stat()
            inode = (stat_info.st_dev, stat_info.st_ino)
            if inode in visited_inodes:
                logger.warning(f"Symlink loop detected at {current_path}. Skipping.")
                return {}
            visited_inodes.add(inode)
        except (OSError, ValueError):
            # In case of stat failure, we proceed cautiously but don't crash
            pass

        try:
            # scandir is faster than os.walk as it retrieves file attributes in one go
            with os.scandir(current_path) as it:
                for entry in it:
                    try:
                        # Skip hidden files/dirs (starting with .) if needed, 
                        # but here we specifically check exclude list for dirs.
                        
                        if entry.is_dir(follow_symlinks=False):
                            if entry.name in self.excluded_dirs:
                                logger.debug(f"Skipping excluded directory: {entry.name}")
                                continue
                            
                            # Recursive call
                            sub_structure = self._recursive_scan(Path(entry.path), visited_inodes)
                            # Only add directory if it's accessible
                            tree_structure[entry.name] = sub_structure
                        
                        elif entry.is_file(follow_symlinks=False):
                            # Files are leaves in the tree, represented as None
                            tree_structure[entry.name] = None
                            
                    except PermissionError:
                        logger.warning(f"Permission denied accessing entry: {entry.path}")
                        continue
                    except OSError as e:
                        logger.error(f"OS error accessing {entry.path}: {e}")
                        continue

        except PermissionError:
            logger.error(f"Permission denied for directory: {current_path}")
        except OSError as e:
            logger.error(f"OS error scanning directory {current_path}: {e}")

        return tree_structure
