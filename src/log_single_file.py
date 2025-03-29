"""
Updates the log with the current cycle count.
"""

import os
import time
import utils # Keep for is_dir_exist for now
import update_custom_log
from config import Config # Import Config

def log_single_cycle(config: Config) -> None:
    """
    Updates the log to reflect the completion of a single cycle.

    Args:
        config: The configuration object.
    """
    # Get paths from config object
    local_log_dir = config.local_log_dir_path
    counter_file = config.cycle_counter_filepath

    # Ensure log directory exists
    if not utils.is_dir_exist(local_log_dir):
        os.makedirs(local_log_dir)

    # Use a file to persist the cycle count.
    try:
        with open(counter_file, "r") as f:
            cycle_count = int(f.read().strip())
    except (FileNotFoundError, ValueError):
        cycle_count = 0
    cycle_count += 1
    with open(counter_file, "w") as f:
        f.write(str(cycle_count))

    timestamp = int(time.time())
    metric_name = "n_cycles"

    # Pass the log directory path from config
    update_custom_log.update_custom_log(
        x=timestamp,
        y=cycle_count,
        name=metric_name,
        log_dir=local_log_dir,
    )
