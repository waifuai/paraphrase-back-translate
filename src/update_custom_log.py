"""
Updates a custom TensorBoard log.
"""

import tensorflow as tf

def update_custom_log(
    x: int,
    y: float,
    name: str,
    log_dir: str,
) -> None:
    """
    Adds a scalar value to the TensorBoard log.

    Args:
        x: The x-axis value (step).
        y: The scalar value to log.
        name: The name of the metric.
        log_dir: The directory where the log file is stored.
    """
    writer = tf.summary.create_file_writer(log_dir)
    with writer.as_default():
        tf.summary.scalar(name, y, step=x)
