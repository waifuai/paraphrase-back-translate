"""
Updates the log with the current cycle count.
"""

import os
import time
import utils
import update_custom_log

def log_single_cycle(
    log_dir_stem: str,
    local_base_dir: str,
) -> None:
    """
    Updates the log to reflect the completion of a single cycle.

    Args:
        log_dir_stem: Base directory name for logs.
        local_base_dir: Base directory (local only).
    """
    local_log_dir = os.path.join(local_base_dir, log_dir_stem)
    if not utils.is_dir_exist(local_log_dir):
        os.makedirs(local_log_dir)

    # Use a file to persist the cycle count.
    counter_file = os.path.join(local_log_dir, "cycle_count.txt")
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

    update_custom_log.update_custom_log(
        x=timestamp,
        y=cycle_count,
        name=metric_name,
        log_dir=local_log_dir,
    )
