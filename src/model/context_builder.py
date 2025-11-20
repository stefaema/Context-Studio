import logging
from pathlib import Path
from typing import List, Optional
from utils.logger import setup_logger

logger = setup_logger(__name__)

class ContextBuilder:
    """
    Responsible for reading file contents and formatting them into a specific
    Markdown structure. Handles encoding issues, file size constraints, 
    and automatic header/footer injection.
    """

    # Safety limit: 1MB. Files larger than this might hang the GUI or LLM context.
    MAX_FILE_SIZE_BYTES = 1_000_000 
    
    # specific filenames for automatic injection
    HEADER_FILENAME = "context_header.md"
    FOOTER_FILENAME = "context_footer.md"

    def build_context_string(self, file_paths: List[Path], root_path: Path) -> str:
        """
        Generates the markdown context string from a list of files.
        
        Structure:
        1. Standard Preamble (Context Injection header)
        2. content of 'context_header.md' (if present in root)
        3. Selected Files (formatted as code blocks)
        4. content of 'context_footer.md' (if present in root)

        Args:
            file_paths: List of absolute paths to files selected in the tree.
            root_path: The project root (used for calculating relative paths and locating headers).

        Returns:
            str: The formatted Markdown string.
        """
        output_parts: List[str] = []

        # 1. Standard Preamble
        # Provides a clear entry point for the LLM.
        output_parts.append("# Context Injection\n")
        output_parts.append("The following codebase context was automatically defined as important for this prompt:\n")

        # 2. Automatic Header Injection
        # We look for the file in the root directory.
        header_path = root_path / self.HEADER_FILENAME
        header_content = self._read_special_file(header_path)
        if header_content:
            output_parts.append(f"{header_content}\n")

        # 3. Selected Files Processing
        for file_path in file_paths:
            # A. Duplication Prevention
            # If the user selected the header/footer in the tree, ignore it here
            # because it is already injected (or will be) outside the code blocks.
            if file_path.name in [self.HEADER_FILENAME, self.FOOTER_FILENAME]:
                continue

            # B. Read Content
            content = self._read_file_safe(file_path)
            
            # C. Skip Empty Files / Failed Reads that resulted in empty strings
            # Note: If _read_file_safe returns an error string "[Error...]", 
            # it is technically 'True' in boolean context, so we include the error.
            # If it returns purely empty string (0 bytes file), we skip.
            if not content:
                continue

            relative_path = self._get_relative_path_safe(file_path, root_path)
            
            # Detect language for code fence
            extension = file_path.suffix.lstrip('.') or "text"
            
            # Format strictly according to requirements:
            # ## File: relative/path
            # ```ext
            # content
            # ```
            header = f"## File: {relative_path}"
            code_block = f"```{extension}\n{content}\n```"
            
            output_parts.append(f"{header}\n{code_block}\n")

        # 4. Automatic Footer Injection
        footer_path = root_path / self.FOOTER_FILENAME
        footer_content = self._read_special_file(footer_path)
        if footer_content:
            # Add a newline before footer to ensure separation
            output_parts.append(f"\n{footer_content}")

        return "\n".join(output_parts)

    def estimate_token_count(self, text: str) -> int:
        """
        Provides a loose estimation of token count.
        
        Args:
            text: The generated context string.
            
        Returns:
            int: Estimated token count.
        """
        if not text:
            return 0
        # Heuristic: Average roughly 4 characters per token for English/Code
        return len(text) // 4

    def _get_relative_path_safe(self, target: Path, root: Path) -> str:
        """Calculates relative path with error handling."""
        try:
            return str(target.relative_to(root).as_posix()) # as_posix for cross-platform consistency
        except ValueError:
            logger.error(f"File {target} is not relative to root {root}")
            return str(target.name)

    def _read_special_file(self, file_path: Path) -> Optional[str]:
        """
        Helper to read header/footer files. 
        Unlike standard files, we do not want to output "[Error...]" tags 
        if the file is simply missing or if there's a read error. 
        We want silent failure for these optional decorators.
        """
        if not file_path.exists() or not file_path.is_file():
            return None
            
        content = self._read_file_safe(file_path)
        
        # If _read_file_safe returned an error tag, treat it as empty for the header/footer
        if content.startswith("[Error"):
            return None
            
        return content.strip()

    def _read_file_safe(self, file_path: Path) -> str:
        """
        Attempts to read a file with multiple encodings and size checks.
        
        Returns:
            str: The file content or a placeholder error message.
        """
        if not file_path.exists():
            # This might happen if a file was deleted after scanning
            logger.warning(f"File not found during read: {file_path}")
            return "[Error: File not found]"

        # 1. Check File Size
        try:
            size = file_path.stat().st_size
            if size > self.MAX_FILE_SIZE_BYTES:
                logger.warning(f"File skipped (too large: {size} bytes): {file_path}")
                return f"[Error: File too large to include ({size} bytes)]"
            if size == 0:
                return "" # Return empty string for 0-byte files
        except OSError as e:
            logger.error(f"Could not stat file {file_path}: {e}")
            return "[Error: Could not access file metadata]"

        # 2. Attempt Read with Encodings
        encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1']
        
        for encoding in encodings_to_try:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue # Try next encoding
            except PermissionError:
                logger.error(f"Permission denied reading file: {file_path}")
                return "[Error: Permission denied]"
            except OSError as e:
                logger.error(f"OS Error reading file {file_path}: {e}")
                return f"[Error: System error {e}]"

        # 3. Fallback if all encodings fail
        logger.warning(f"Could not decode file: {file_path}")
        return "[Error: Binary or unsupported encoding]"
