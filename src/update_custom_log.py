"""
Logs metrics using the standard Python logging module.
"""

import logging

# Logger instance (will inherit configuration from the root logger)
logger = logging.getLogger(__name__)

def update_custom_log(
    x: int,
    y: float,
    name: str,
) -> None:
    """
    Logs a scalar metric value using the configured logger.

    Args:
        x: The step or index value (e.g., cycle number).
        y: The scalar value to log.
        name: The name of the metric.
    """
    # Log using standard INFO level. The actual handler (file/console) is configured elsewhere.
    logger.info(f"Metric - Step: {x}, Name: {name}, Value: {y}")

# Removed dependency on log_dir as configuration is handled globally.
