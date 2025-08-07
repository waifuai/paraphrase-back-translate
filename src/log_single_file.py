"""
Logs the completion of a cycle using standard Python logging.
"""

import os
import logging
from . import update_custom_log
from .config import Config # Import Config

# --- Logging Configuration Flag ---
_logger_configured = False
# Get logger for this module
logger = logging.getLogger(__name__)

def setup_logging(log_filepath: str):
    """Configures the root logger to log to a file and console, ensuring it happens only once."""
    global _logger_configured
    if not _logger_configured:
        try:
            # Ensure the directory exists
            log_dir = os.path.dirname(log_filepath)
            os.makedirs(log_dir, exist_ok=True)

            log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # File Handler
            file_handler = logging.FileHandler(log_filepath, encoding='utf-8') # Specify encoding
            file_handler.setFormatter(log_formatter)

            # Console Handler
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(log_formatter)

            # Get root logger, remove existing handlers (important for re-runs), add new ones
            root_logger = logging.getLogger()
            # Clear existing handlers to prevent duplicates if script is run multiple times in same process
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)
                handler.close() # Close handlers before removing

            root_logger.addHandler(file_handler)
            root_logger.addHandler(console_handler)
            root_logger.setLevel(logging.INFO) # Set level on the root logger

            _logger_configured = True
            # Use the root logger to announce configuration success
            logging.info(f"Logging configured. Log file: {log_filepath}")

        except Exception as e:
            # Fallback to basic console logging if setup fails
            logging.basicConfig(level=logging.ERROR)
            logging.error(f"Failed to configure file logging to {log_filepath}: {e}. Falling back to console logging.")
            _logger_configured = True # Mark as configured to prevent retries

# --- Cycle Tracking (In-memory) ---
_current_cycle_count = 0

def log_single_cycle(config: Config) -> None:
    """
    Logs the completion of a single cycle using the configured logger.

    Args:
        config: The configuration object.
    """
    global _current_cycle_count
    _current_cycle_count += 1

    # Ensure logging is set up using the path from config
    # setup_logging is also called in main.py, but calling here ensures it's
    # configured before the first cycle log if main.py's call failed or was skipped.
    setup_logging(config.log_filepath) # Configure logger if not already done

    # Log the cycle completion using the updated update_custom_log
    metric_name = "cycle_completed"
    update_custom_log.update_custom_log(
        x=_current_cycle_count,
        y=_current_cycle_count, # Logging the count itself as the metric value
        name=metric_name,
    )
    # Use the module-specific logger for cycle completion message
    logger.info(f"--- Cycle {_current_cycle_count} completed. ---")

# Removed old file-based cycle counter logic
