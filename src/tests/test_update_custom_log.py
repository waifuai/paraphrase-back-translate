# tests/test_update_custom_log.py
import unittest
from unittest.mock import patch, MagicMock
import update_custom_log
import tensorflow as tf

class TestUpdateCustomLog(unittest.TestCase):
    @patch('tensorflow.summary.scalar') # Also mock the scalar function
    @patch('tensorflow.summary.create_file_writer')
    def test_update_custom_log(self, mock_create_file_writer, mock_scalar): # Add mock_scalar arg
        # Mock the file writer and its context manager.
        mock_writer = MagicMock()
        mock_create_file_writer.return_value = mock_writer
        mock_writer_context = MagicMock()
        mock_writer.__enter__.return_value = mock_writer_context

        update_custom_log.update_custom_log(x=1, y=2.5, name="test_metric", log_dir="test_log_dir")

        mock_create_file_writer.assert_called_once_with("test_log_dir")
        mock_writer.as_default.assert_called_once() # context manager was used
        # Assert on the mock object now
        mock_scalar.assert_called_once_with("test_metric", 2.5, step=1)