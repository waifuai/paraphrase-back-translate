"""
Logs the completion of a cycle using standard Python logging.
"""

import os
import time
import logging
import update_custom_log
from config import Config # Import Config

# --- Logging Configuration Flag ---
_logger_configured = False

def setup_logging(log_filepath: str):
    """Configures the root logger to log to a file, ensuring it happens only once."""
    global _logger_configured
    if not _logger_configured:
        # Ensure the directory exists
        log_dir = os.path.dirname(log_filepath)
        os.makedirs(log_dir, exist_ok=True)

        log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler = logging.FileHandler(log_filepath)
        file_handler.setFormatter(log_formatter)

        # Get root logger, remove existing handlers, add new one
        root_logger = logging.getLogger()
        # Clear existing handlers to prevent duplicates if script is run multiple times in same process
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        root_logger.addHandler(file_handler)
        root_logger.setLevel(logging.INFO)

        # Also add a console handler for visibility during execution
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        root_logger.addHandler(console_handler)

        _logger_configured = True
        logging.info(f"Logging configured. Log file: {log_filepath}") # Use logging to announce config

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

    # Ensure logging is set up
    log_filepath = os.path.join(config.local_log_dir_path, "backtranslate.log")
    setup_logging(log_filepath) # Configure logger if not already done

    # Log the cycle completion using the updated update_custom_log
    metric_name = "cycle_completed"
    update_custom_log.update_custom_log(
        x=_current_cycle_count,
        y=_current_cycle_count, # Logging the count itself as the metric value
        name=metric_name,
    )
    logging.info(f"--- Cycle {_current_cycle_count} completed. ---")
