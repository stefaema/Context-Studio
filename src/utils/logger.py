import logging
import sys
from pathlib import Path

def setup_logger(name: str, log_file: Path = Path("context_studio.log")) -> logging.Logger:
    """
    Configures and returns a logger instance with both file and console handlers.
    
    Args:
        name: The name of the logger (usually __name__).
        log_file: Path to the log output file.

    Returns:
        logging.Logger: Configured logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    # Prevent adding handlers multiple times if setup is called repeatedly
    if not logger.handlers:
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # File Handler (Detailed)
        try:
            fh = logging.FileHandler(log_file, mode='a', encoding='utf-8')
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(formatter)
            logger.addHandler(fh)
        except (PermissionError, OSError) as e:
            sys.stderr.write(f"CRITICAL: Could not setup file logging: {e}\n")

        # Console Handler (Info and above)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    return logger
