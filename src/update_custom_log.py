"""
Logs metrics using the standard Python logging module.
"""

import logging

# Logger instance (will be configured elsewhere, e.g., in main or log_single_file)
logger = logging.getLogger(__name__)

def update_custom_log(
    x: int,
    y: float,
    name: str,
    # log_dir: str, # Removed - Logger configuration handles destination
) -> None:
    """
    Logs a scalar metric value using the configured logger.

    Args:
        x: The step or index value.
        y: The scalar value to log.
        name: The name of the metric.
    """
    # Example log format, adjust as needed
    logger.info(f"Metric - Step: {x}, Name: {name}, Value: {y}")
