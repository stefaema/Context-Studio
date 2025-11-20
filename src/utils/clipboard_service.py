import pyperclip
from typing import Tuple
from utils.logger import setup_logger

# Initialize logger for this module
logger = setup_logger(__name__)

class ClipboardService:
    """
    A defensive wrapper around the system clipboard mechanism.
    Ensures the application does not crash if OS clipboard dependencies 
    (e.g., xclip/xsel on Linux) are missing.
    """

    @staticmethod
    def copy_text(text: str) -> Tuple[bool, str]:
        """
        Attempts to copy the provided text to the system clipboard.

        Args:
            text (str): The string content to copy.

        Returns:
            Tuple[bool, str]: A tuple containing:
                - bool: True if successful, False otherwise.
                - str: A user-friendly status message or error description.
        """
        # 1. Validation: Empty content
        if not text:
            logger.warning("Clipboard copy aborted: Input text is empty.")
            return False, "Nothing to copy."

        # 2. Execution: Attempt copy with error handling
        try:
            pyperclip.copy(text)
            logger.info("Text successfully copied to clipboard.")
            return True, "Copied to clipboard!"

        except pyperclip.PyperclipException as e:
            # Specific handling for missing system dependencies (common on minimal Linux)
            error_msg = "Clipboard failed: Missing system dependency (install xclip or xsel)."
            logger.error(f"{error_msg} Details: {e}")
            return False, error_msg

        except Exception as e:
            # Generic fallback for unexpected OS errors
            error_msg = f"Clipboard failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, "Clipboard error occurred."
