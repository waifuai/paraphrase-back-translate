# tests/test_update_custom_log.py
import unittest
from unittest.mock import patch, MagicMock
import update_custom_log
# import tensorflow as tf # Removed TF import
import logging # Import logging

class TestUpdateCustomLog(unittest.TestCase):
    # Patch the logger instance within the update_custom_log module
    @patch('update_custom_log.logger')
    def test_update_custom_log(self, mock_logger):
        # No need to mock file writer or scalar anymore

        test_x = 1
        test_y = 2.5
        test_name = "test_metric"
        expected_log_message = f"Metric - Step: {test_x}, Name: {test_name}, Value: {test_y}"

        # Call the function (log_dir is no longer an argument)
        update_custom_log.update_custom_log(x=test_x, y=test_y, name=test_name)

        # Assert that the logger's info method was called with the correct message
        mock_logger.info.assert_called_once_with(expected_log_message)

        # Remove old TF assertions
        # mock_create_file_writer.assert_called_once_with("test_log_dir")
        # mock_writer.as_default.assert_called_once() # context manager was used
        # mock_scalar.assert_called_once_with("test_metric", 2.5, step=1)